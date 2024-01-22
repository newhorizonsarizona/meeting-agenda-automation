import sys
import os
import asyncio
import datetime
import json
import time
from o365.util.constants import Constants
from o365.util.meeting_util import MeetingUtil
from o365.util.date_util import DateUtil
from o365.auth.auth_helper import AuthHelper
from o365.drive.drive_helper import DriveHelper
from o365.excel.excel_helper import ExcelHelper
from o365.excel.range_assignments import RangeAssignments
from o365.excel.range_assignments_reverse import RangeAssignmentsReverse
from o365.exception.agenda_exception import AgendaException
from o365.user.user_helper import UserHelper
from o365.planner.planner_helper import PlannerHelper
from o365.graph.graph_helper import GraphHelper


class AgendaCreator:
    """This class is used for creating the agenda"""

    _next_tuesday: datetime
    _next_tuesday_date: str
    _next_tuesday_date_us: str
    _next_tuesday_month: str
    _next_tuesday_meeting_docs: str
    _next_tuesday_meeting_agenda_excel: str
    _agenda_template_excel: str
    _is_next_meeting_reverse: bool

    def __init__(self, today_date: str = None) -> None:
        """initialize the agenda creator"""
        date_util: DateUtil = DateUtil(today_date)
        self._next_tuesday = date_util.next_tuesday
        self._next_tuesday_date = date_util.next_tuesday_date
        self._next_tuesday_date_us = date_util.next_tuesday_date_us
        self._next_tuesday_month = date_util.next_tuesday_month
        meeting_util = MeetingUtil(self._next_tuesday)
        self._next_tuesday_meeting_docs = meeting_util.next_tuesday_meeting_docs
        self._next_tuesday_meeting_agenda_excel = meeting_util.next_tuesday_meeting_agenda_excel
        self._agenda_template_excel = meeting_util.agenda_template_excel
        self._is_next_meeting_reverse = meeting_util.is_next_meeting_reverse

    def get_assigned_to_user(self, graph_client, task):
        """Gets assigned to user for task"""
        retry_count = 0
        assigned_to_user = None
        while retry_count < 5:
            try:
                print(f"Getting the assigned to user for task: {task.title}")
                assigned_to_users = list(task.assignments.additional_data.keys())
                if assigned_to_users is not None and len(assigned_to_users) > 0:
                    assigned_to_user_id = list(task.assignments.additional_data.keys())[0]
                    user = asyncio.run(UserHelper.get_user(graph_client, assigned_to_user_id))
                    if user is not None:
                        return user
                else:
                    return assigned_to_user
            except RuntimeError as e:
                if "Event loop is closed" in str(e):
                    if retry_count < 5:
                        retry_count = retry_count + 1
                        time.sleep(10)
                    else:
                        print(e)
                        break  # do something here, like log the error
        return assigned_to_user

    def get_drive(self, graph_client, group_id):
        """Gets the drive for the specified group_id"""
        retry_count = 0
        drive_4_group = None
        while retry_count < 3:
            try:
                print(f"Getting the drive for group: {group_id}")
                drive = asyncio.run(DriveHelper.get_drive(graph_client, group_id))
                if drive:
                    return drive
            except RuntimeError as e:
                if "Event loop is closed" in str(e):
                    if retry_count < 5:
                        retry_count = retry_count + 1
                        time.sleep(10)
                    else:
                        print(e)
                        break  # do something here, like log the error
        return drive_4_group

    def _create_weekly_meeting_docs(self, graph_client, drive_id, item_id, meeting_docs_folder):
        """Create the weekly meeting docs folder"""
        retry_count = 0
        folder_item_id = None
        while retry_count < 5:
            try:
                print(f"Creating the folder {meeting_docs_folder} for drive item: {item_id}")
                folder_item = asyncio.run(
                    DriveHelper.create_folder(graph_client, drive_id, item_id, meeting_docs_folder)
                )
                if folder_item and folder_item.id:
                    return folder_item.id
            except RuntimeError as e:
                if "Event loop is closed" in str(e):
                    if retry_count < 5:
                        retry_count = retry_count + 1
                        time.sleep(10)

        return folder_item_id

    # GET /drives/{drive-id}/root/search(q=\'FolderName\')?$filter=item ne null&$select=name,id,webUrl'
    def search_item_with_name(self, drive_id: str, item_name: str):
        """Search the the drive id for matching item"""
        try:
            print(f"Searching the item matching {item_name} in drive {drive_id}")
            graph_helper: GraphHelper = GraphHelper()
            item = graph_helper.get_request(
                f"/drives/{drive_id}/root/search(q='{item_name}')?$select=name,id,webUrl",
                {"Content-Type": "application/json"},
            )
            if item and item["value"] is not None:
                for value in item["value"]:
                    if value["name"] == item_name:
                        print(f"Found item {value['name']}")
                        return value
        except Exception as e:
            print(f"Error: {e}")
        return None

    # POST /drives/{drive-id}/items/{item-id}/copy'
    def _copy_agenda_to_meeting_folder(
        self,
        graph_client,
        drive_id: str,
        template_item_id: str,
        meeting_folder_item_id: str,
        meeting_agenda_excel_name: str,
    ):
        """Copy agenda template to the meeting folder"""
        retry_count = 0
        agenda_item = None
        while retry_count < 10:
            try:
                print(f"Copying the agenda template {template_item_id} to meeting folder: {meeting_folder_item_id}")
                copy_status = asyncio.run(
                    DriveHelper.copy_item(
                        graph_client,
                        drive_id,
                        template_item_id,
                        meeting_folder_item_id,
                        meeting_agenda_excel_name,
                    )
                )
                if copy_status:
                    return copy_status
            except RuntimeError as e:
                if "Event loop is closed" in str(e):
                    if retry_count < 10:
                        retry_count = retry_count + 1
                        time.sleep(10)
            except Exception as ex:
                if "DeserializationError" in str(ex):
                    time.sleep(30)

        return agenda_item

    def _do_next_meeting_docs_item_id(
        self,
        graph_client,
        drive_id,
        wmc_drive_item_id,
        meeting_docs_folder,
        is_create_not_exist: bool,
    ):
        """Searches and/or creates the next meeting docs folder and returns the item"""
        retry = 0
        while True:
            meeting_docs_folder_item = self.search_item_with_name(drive_id, meeting_docs_folder)
            if meeting_docs_folder_item is not None:
                return meeting_docs_folder_item
            if is_create_not_exist and retry == 0:
                meeting_docs_folder_item_id = self._create_weekly_meeting_docs(
                    graph_client, drive_id, wmc_drive_item_id, meeting_docs_folder
                )
            retry = retry + 1
            if retry < 30:
                time.sleep(30)
            else:
                raise AgendaException(f"Could not find the id for the meeting docs folder {meeting_docs_folder}")

    def _do_next_meeting_agenda_excel_item_id(
        self,
        graph_client,
        drive_id,
        ma_agenda_template_item_id,
        meeting_docs_folder_item_id,
        is_copy_not_exist: bool,
    ):
        """Search and/or copy the next meeting agenda excel file and returns the item"""
        retry = 0
        while True:
            next_meeting_agenda_excel_item = self.search_item_with_name(
                drive_id, self._next_tuesday_meeting_agenda_excel
            )
            if next_meeting_agenda_excel_item is not None:
                return next_meeting_agenda_excel_item
            if is_copy_not_exist and retry == 0:
                next_meeting_agenda_excel_item_id = self._copy_agenda_to_meeting_folder(
                    graph_client,
                    drive_id,
                    ma_agenda_template_item_id,
                    meeting_docs_folder_item_id,
                    self._next_tuesday_meeting_agenda_excel,
                )
            retry = retry + 1
            if retry < 30:
                time.sleep(30)
            else:
                raise AgendaException(
                    f"Could not find the id for the next meeting agenda excel {self._next_tuesday_meeting_agenda_excel}"
                )

    # GET /drives/{drive-id}/items/{id}/workbook/worksheets/
    def _get_agenda_worksheet_id(self, graph_client, drive_id, item_id):
        """Create the Agenda worksheet id"""
        retry_count = 0
        excel_worksheet_id = None
        while retry_count < 10:
            try:
                print(f"Getting the agenda worksheet id for drive item: {item_id}")
                worksheets = asyncio.run(ExcelHelper.get_worksheets(graph_client, drive_id, item_id))
                if worksheets and worksheets.value:
                    for worksheet in worksheets.value:
                        if worksheet.name == "Agenda":
                            return worksheet.id
            except RuntimeError as e:
                if "Event loop is closed" in str(e):
                    if retry_count < 10:
                        retry_count = retry_count + 1
                        time.sleep(10)
                    else:
                        raise e
        return excel_worksheet_id

    # PATCH /drives/{drive-id}/items/{id}/workbook/worksheets/{id|name}/range(address='A1:A2')
    # {
    #    "values" : [["Hello", "100"],["1/1/2016", null]],
    #    "formulas" : [[null, null], [null, "=B1*2"]],
    #    "numberFormat" : [[null,null], ["m-ddd", null]]
    # }
    def _update_agenda_worksheet_range(self, drive_id, item_id, worksheet_id, range_address, range_data: dict):
        """Get the worksheet range"""
        try:
            print(
                f"Updating the worksheet range {range_address} for item {item_id} and worksheeet{worksheet_id} in drive {drive_id}"
            )
            graph_helper: GraphHelper = GraphHelper()
            data_json = json.dumps(range_data)
            print(data_json)
            range_update_result = graph_helper.patch_request(
                f"/drives/{drive_id}/items/{item_id}/workbook/worksheets/{worksheet_id}/range(address='{range_address}')",
                data_json,
                {"Content-Type": "application/json"},
            )
            if range_update_result:
                print(f"Range update result {range_update_result}")
                return range_update_result
        except AgendaException as e:
            print(f"Error: {e}")
        return None

    def _populate_agenda_worksheet(self, drive_id, item_id, worksheet_id, range_assignments_map: dict):
        """Populating the agenda worksheet based on specified range asssignments"""
        for range_key, range_value in range_assignments_map.items():
            range_data: dict = {
                "values": range_value["values"],
                "formulas": range_value["formulas"],
                "numberFormat": range_value["formats"],
            }
            self._update_agenda_worksheet_range(drive_id, item_id, worksheet_id, range_key, range_data)
            time.sleep(2)

    def create(self):
        """Get the planner tasks for next meeting"""
        print("Creating agenda")
        try:
            graph_client = AuthHelper.graph_service_client_with_adapter()
            drive = self.get_drive(graph_client, Constants.GROUP_IDS[0])
            print(f"Drive id: {drive.id}")
            meeting_docs_folder = self._next_tuesday_meeting_docs
            wmc_drive_item = self.search_item_with_name(drive.id, "Weekly Meeting Channel")
            wmc_drive_item_id = wmc_drive_item["id"]
            print(f"Weekly Meeting Channel Drive Item Id: {wmc_drive_item_id}")

            meeting_docs_folder_item_id = self._do_next_meeting_docs_item_id(
                graph_client, drive.id, wmc_drive_item_id, meeting_docs_folder, True
            )["id"]
            print(f"Meeting Docs folder Item Id: {meeting_docs_folder_item_id}")

            ma_agenda_template_item = self.search_item_with_name(drive.id, self._agenda_template_excel)
            if ma_agenda_template_item is not None:
                ma_agenda_template_item_id = ma_agenda_template_item["id"]
            print(f"NHTM Agenda Template Excel Item Id: {ma_agenda_template_item_id}")

            next_meeting_agenda_excel_item_id = self._do_next_meeting_agenda_excel_item_id(
                graph_client,
                drive.id,
                ma_agenda_template_item_id,
                meeting_docs_folder_item_id,
                True,
            )["id"]
            print(f"Next Tuesday Meeting Agenda Excel Item Id: {next_meeting_agenda_excel_item_id}")

            agenda_worksheet_id = self._get_agenda_worksheet_id(
                graph_client, drive.id, next_meeting_agenda_excel_item_id
            )
            print(f"Updating Agenda worksheet: {agenda_worksheet_id}")
            for group_id in Constants.GROUP_IDS:
                plan = PlannerHelper.get_plan_by_name(graph_client, group_id, self._next_tuesday_month[:3].lower())
                if plan is None:
                    print(f"No matching plan found next week in group {group_id}")
                    continue
                bucket = PlannerHelper.get_bucket_by_name(graph_client, plan.id, self._next_tuesday_date)
                if bucket is None:
                    print(f"No matching bucket found for next week in plan {plan.id}")
                    exit(1)
                tasks = PlannerHelper.fetch_tasks_in_bucket(graph_client, bucket.id)
                if tasks is None:
                    print("No matching tasks found for next the meeting next week")
                    exit(1)
                meeting_assignments: dict = {}
                for task in tasks.value:
                    assigned_to_user = self.get_assigned_to_user(graph_client, task)
                    if assigned_to_user is not None:
                        print(f"{task.title}, due {task.due_date_time} is assigned to {assigned_to_user.display_name}")
                        meeting_assignments[task.title.strip()] = assigned_to_user.display_name
                meeting_assignments["Meeting Day"] = "Tuesday"
                meeting_assignments["Meeting Date"] = self._next_tuesday_date_us
                range_assignments: RangeAssignments = (
                    RangeAssignments() if not self._is_next_meeting_reverse else RangeAssignmentsReverse()
                )
                range_assignments_map: dict = range_assignments.populate_values(meeting_assignments)
                print(range_assignments_map)
                self._populate_agenda_worksheet(
                    drive.id,
                    next_meeting_agenda_excel_item_id,
                    agenda_worksheet_id,
                    range_assignments_map,
                )
                print(f"Successfully created the agenda for the next meeting on {self._next_tuesday_date}")
                return
        except RuntimeError as e:
            print(f"Error creating agenda. {e}")

        print("No matching plan or buckets were found for next the meeting next week")
        exit(1)
