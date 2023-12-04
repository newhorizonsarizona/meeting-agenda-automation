import os
import asyncio
import datetime
import json
import time
from auth.auth_helper import AuthHelper
from drive.drive_helper import DriveHelper
from excel.excel_helper import ExcelHelper
from excel.range_assignments import RangeAssignments
from excel.range_assignments_reverse import RangeAssignmentsReverse
from exception.agenda_exception import AgendaException
from teams.weekly_meeting_message import WeeklyMeetingMessage
from teams.teams_helper import TeamsHelper
from user.user_helper import UserHelper
from planner.planner_helper import PlannerHelper
from graph.graph_helper import GraphHelper
from teams.teams_helper import TeamsHelper

group_ids = [
    "aa235df6-19fc-4de3-8498-202b5cbe2d15",
    "1ab26305-df89-435b-802d-4f223a037771",
]


class AgendaCreator:
    """This class is used for creating the agenda"""

    def _get_next_meeting_plan(self, graph_client, group_id):
        """Gets plans for the specified group_id"""
        retry_count = 0
        next_meeting_plan = None
        while retry_count < 3:
            try:
                print(f"Getting the plan for next meeting in group: {group_id}")
                plans = asyncio.run(PlannerHelper.get_all_plans(graph_client, group_id))
                if plans and plans.value:
                    for plan in plans.value:
                        if self._next_tuesday_month[:3].lower() in plan.title.lower():
                            print(f"Found next weeks plan {plan}")
                            return plan
            except RuntimeError as e:
                if "Event loop is closed" in str(e):
                    if retry_count < 3:
                        retry_count = retry_count + 1
                        time.sleep(10)
                    else:
                        print(e)
                        break  # do something here, like log the error
        return next_meeting_plan

    def _get_next_meeting_bucket(self, graph_client, plan):
        """Gets buckets for the specified plan"""
        retry_count = 0
        next_meeting_bucket = None
        next_tuesday_date = self._next_tuesday_date
        while retry_count < 5:
            try:
                print(
                    f"Getting the bucket for {next_tuesday_date} in plan: {plan.title} ({plan.id})"
                )
                buckets = asyncio.run(
                    PlannerHelper.get_all_buckets(graph_client, plan.id)
                )
                if buckets and buckets.value:
                    for bucket in buckets.value:
                        if self._next_tuesday_date in bucket.name:
                            print(f"Found next weeks bucket {bucket}")
                            return bucket
            except RuntimeError as e:
                if "Event loop is closed" in str(e):
                    if retry_count < 5:
                        retry_count = retry_count + 1
                        time.sleep(10)
                    else:
                        print(e)
                        break  # do something here, like log the error
        return next_meeting_bucket

    def _get_next_meeting_tasks(self, graph_client, bucket):
        """Gets tasks in the specified bucket"""
        retry_count = 0
        next_meeting_tasks = None
        while retry_count < 5:
            try:
                print(f"Getting the tasks in bucket: {bucket.name} ({bucket.id})")
                tasks = asyncio.run(
                    PlannerHelper.get_tasks_in_bucket(graph_client, bucket.id)
                )
                if tasks and tasks.value:
                    return tasks
            except RuntimeError as e:
                if "Event loop is closed" in str(e):
                    if retry_count < 5:
                        retry_count = retry_count + 1
                        time.sleep(10)
                    else:
                        print(e)
                        break  # do something here, like log the error
        return next_meeting_tasks

    def _get_assigned_to_user(self, graph_client, task):
        """Gets assigned to user for task"""
        retry_count = 0
        assigned_to_user = None
        while retry_count < 5:
            try:
                print(f"Getting the assigned to user for task: {task.title}")
                assigned_to_users = list(task.assignments.additional_data.keys())
                if assigned_to_users is not None and len(assigned_to_users) > 0:
                    assigned_to_user_id = list(task.assignments.additional_data.keys())[
                        0
                    ]
                    user = asyncio.run(
                        UserHelper.get_user(graph_client, assigned_to_user_id)
                    )
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

    def _get_drive(self, graph_client, group_id):
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

    def _get_children_for_path(self, graph_client, drive_id, children, path):
        """Gets the children for the specified path"""
        retry_count = 0
        children_for_path = None
        while retry_count < 3:
            try:
                # print(f'Getting the children for path: {path}')
                path_items = path.split("/")
                if path_items:
                    for child in children.value:
                        print(
                            f"Getting the child: {child.name}, matching with path {path_items[0]}"
                        )
                        if child.name == path_items[0]:
                            print(f"Getting the children for path: {child.name}")
                            children = asyncio.run(
                                DriveHelper.get_children_by_item(
                                    graph_client, drive_id, child.id
                                )
                            )
                            if len(path_items) > 1:
                                next_path = "/".join(path_items[1:])
                                print(f"Looking in {next_path}")
                                children = self._get_children_for_path(
                                    graph_client, drive_id, children, next_path
                                )
                            # print(children)
                return children
            except RuntimeError as e:
                if "Event loop is closed" in str(e):
                    if retry_count < 5:
                        retry_count = retry_count + 1
                        time.sleep(10)
                    else:
                        print(e)
                        break  # do something here, like log the error
        return children_for_path

    def _get_drive_item_id_for_path(self, graph_client, drive_id, item_id, path):
        """Gets the drive item id for the specified path"""
        retry_count = 0
        drive_item_id = None
        while retry_count < 3:
            try:
                # print(f'Getting the children for path: {path}')
                path_items = path.split("/")
                print(path_items)
                if path_items:
                    children = asyncio.run(
                        DriveHelper.get_children_by_item(
                            graph_client, drive_id, item_id
                        )
                    )
                    for child in children.value:
                        print(
                            f"Getting the child: {child.name}, matching with path {path_items[0]}"
                        )
                        if child.name == path_items[0]:
                            print(f"The item id for {child.name} is {child.id}")
                            drive_item_id = child.id
                            if len(path_items) > 1:
                                next_path = "/".join(path_items[1:])
                                print(f"Looking in {next_path}")
                                drive_item_id = self._get_drive_item_id_for_path(
                                    graph_client, drive_id, child.id, next_path
                                )
                        return drive_item_id
            except RuntimeError as e:
                if "Event loop is closed" in str(e):
                    if retry_count < 5:
                        retry_count = retry_count + 1
                        time.sleep(10)
                    else:
                        print(e)
                        break  # do something here, like log the error
        return drive_item_id

    def _get_drive_item_id(self, graph_client, drive_id, path):
        """Gets the drive for the specified group_id"""
        retry_count = 0
        drive_item_id = None
        while retry_count < 3:
            try:
                print(f"Getting the drive item id for drive: {drive_id}")
                root_children = asyncio.run(
                    DriveHelper.get_children_by_path(graph_client, drive_id)
                )  # 3 = Weekly Meeting Channel id
                if root_children and root_children.value:
                    for root_child in root_children.value:
                        path_items = path.split("/")
                        if path_items[0] == root_child.name:
                            print(f"Getting the item id for path: {path}")
                            drive_item_id = root_child.id
                            if len(path_items) > 1:
                                next_path = "/".join(path_items[1:])
                                print(f"Looking in {next_path}")
                                drive_item_id = self._get_drive_item_id_for_path(
                                    graph_client, drive_id, drive_item_id, next_path
                                )
                            return drive_item_id
            except RuntimeError as e:
                if "Event loop is closed" in str(e):
                    if retry_count < 5:
                        retry_count = retry_count + 1
                        time.sleep(10)
                    else:
                        print(e)
                        break  # do something here, like log the error
        return drive_item_id

    def _create_weekly_meeting_docs(
        self, graph_client, drive_id, item_id, meeting_docs_folder
    ):
        """Create the weekly meeting docs folder"""
        retry_count = 0
        folder_item_id = None
        while retry_count < 5:
            try:
                print(
                    f"Creating the folder {meeting_docs_folder} for drive item: {item_id}"
                )
                folder_item = asyncio.run(
                    DriveHelper.create_folder(
                        graph_client, drive_id, item_id, meeting_docs_folder
                    )
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
    def _search_item_with_name(self, drive_id: str, item_name: str):
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
        while retry_count < 5:
            try:
                print(
                    f"Copying the agenda template {template_item_id} to meeting folder: {meeting_folder_item_id}"
                )
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
                    if retry_count < 5:
                        retry_count = retry_count + 1
                        time.sleep(10)
            except Exception as ex:
                if "DeserializationError" in str(ex):
                    time.sleep(30)

        return agenda_item

    # GET /drives/{drive-id}/items/{id}/workbook/worksheets/
    def _get_agenda_worksheet_id(self, graph_client, drive_id, item_id):
        """Create the Agenda worksheet id"""
        retry_count = 0
        excel_worksheet_id = None
        while retry_count < 3:
            try:
                print(f"Getting the agenda worksheet id for drive item: {item_id}")
                worksheets = asyncio.run(
                    ExcelHelper.get_worksheets(graph_client, drive_id, item_id)
                )
                if worksheets and worksheets.value:
                    for worksheet in worksheets.value:
                        if worksheet.name == "Agenda":
                            return worksheet.id
            except RuntimeError as e:
                if "Event loop is closed" in str(e):
                    if retry_count < 5:
                        retry_count = retry_count + 1
                        time.sleep(10)
                    else:
                        raise e
        return excel_worksheet_id

    # GET /drives/{drive-id}/items/{id}/workbook/worksheets/{id|name}/cell(row=<row>,column=<column>)
    def _get_agenda_worksheet_cell(self, drive_id, item_id, worksheet_id, row, column):
        """Get the worksheet cell"""
        try:
            print(
                f"Getting the worksheet cell for item {item_id} and worksheeet{worksheet_id} in drive {drive_id}"
            )
            graph_helper: GraphHelper = GraphHelper()
            cell = graph_helper.get_request(
                f"/drives/{drive_id}/items/{item_id}/workbook/worksheets/{worksheet_id}/cell(row={row},column={column})",
                {"Content-Type": "application/json"},
            )
            if cell:
                print(f"Found cell {cell}")
                return cell
        except Exception as e:
            print(f"Error: {e}")
        return None

    # GET /drives/{drive-id}/items/{id}/workbook/worksheets/{id|name}/range(address='A1:A2')
    def _get_agenda_worksheet_range(
        self, drive_id, item_id, worksheet_id, range_address
    ):
        """Get the worksheet range"""
        try:
            print(
                f"Getting the worksheet range {range_address} for item {item_id} and worksheeet{worksheet_id} in drive {drive_id}"
            )
            graph_helper: GraphHelper = GraphHelper()
            range_values = graph_helper.get_request(
                f"/drives/{drive_id}/items/{item_id}/workbook/worksheets/{worksheet_id}/range(address='{range_address}')",
                {"Content-Type": "application/json"},
            )
            if range_values:
                print(f"Found range {range_values}")
                return range_values
        except Exception as e:
            print(f"Error: {e}")
        return None

    # PATCH /drives/{drive-id}/items/{id}/workbook/worksheets/{id|name}/range(address='A1:A2')
    # {
    #    "values" : [["Hello", "100"],["1/1/2016", null]],
    #    "formulas" : [[null, null], [null, "=B1*2"]],
    #    "numberFormat" : [[null,null], ["m-ddd", null]]
    # }
    def _update_agenda_worksheet_range(
        self, drive_id, item_id, worksheet_id, range_address, range_data: dict
    ):
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

    def _populate_agenda_worksheet(
        self, drive_id, item_id, worksheet_id, range_assignments_map: dict
    ):
        """Populating the agenda worksheet based on specified range asssignments"""
        for range_key, range_value in range_assignments_map.items():
            range_data: dict = {
                "values": range_value["values"],
                "formulas": range_value["formulas"],
                "numberFormat": range_value["formats"],
            }
            self._update_agenda_worksheet_range(
                drive_id, item_id, worksheet_id, range_key, range_data
            )
            time.sleep(2)

    # GET /teams/{team-id}/channels
    def _get_teams_channel(
        self, graph_client, team_id, channel_name
    ):
        """Get the teams channel"""
        retry_count = 0
        channel_item = None
        while retry_count < 5:
            try:
                print(
                    f"Getting the channel {channel_name} for team: {team_id}"
                )
                channels = asyncio.run(
                    TeamsHelper.get_channels(
                        graph_client, team_id
                    )
                )
                if channels and channels.value:
                    for channel in channels.value:
                        if channel.displayName == channel_name:
                            return channel
            except RuntimeError as e:
                if "Event loop is closed" in str(e):
                    if retry_count < 5:
                        retry_count = retry_count + 1
                        time.sleep(10)

        return channel_item

    # GET /teams/{team-id}/channels/{channel-id}/messages
    def _post_message_to_channel(
        self, graph_client, team_id, channel_id, message, subject, attachment_url
    ):
        """Post the message to a teams channel"""
        retry_count = 0
        message_item = None
        while retry_count < 5:
            try:
                print(
                    f"Posting message to channel {channel_id} for team: {team_id}"
                )
                message = asyncio.run(
                    TeamsHelper.post_message(
                        graph_client, team_id, channel_id, message, subject, attachment_url
                    )
                )
                if message:
                    return message
            except RuntimeError as e:
                if "Event loop is closed" in str(e):
                    if retry_count < 5:
                        retry_count = retry_count + 1
                        time.sleep(10)

        return message_item

    def create(self):
        """Get the planner tasks for next meeting"""
        print("Creating agenda")
        try:
            graph_client = AuthHelper.graph_service_client_with_adapter()
            drive = self._get_drive(
                graph_client, "aa235df6-19fc-4de3-8498-202b5cbe2d15"
            )
            print(f"Drive id: {drive.id}")
            meeting_docs_folder = self._next_tuesday_meeting_docs
            wmc_drive_item = self._search_item_with_name(
                drive.id, "Weekly Meeting Channel"
            )
            wmc_drive_item_id = wmc_drive_item["id"]
            print(f"Weekly Meeting Channel Drive Item Id: {wmc_drive_item_id}")
            retry = 0
            while True:
                meeting_docs_folder_item = self._search_item_with_name(
                    drive.id, meeting_docs_folder
                )
                if meeting_docs_folder_item is not None:
                    meeting_docs_folder_item_id = meeting_docs_folder_item["id"]
                    meeting_docs_folder_item_url = meeting_docs_folder_item["webUrl"]
                    if meeting_docs_folder_item_id is not None:
                        break
                if retry == 0:
                    meeting_docs_folder_item_id = self._create_weekly_meeting_docs(
                        graph_client, drive.id, wmc_drive_item_id, meeting_docs_folder
                    )
                retry = retry + 1
                if retry < 30:
                    time.sleep(30)
                else:
                    raise AgendaException(
                        f"Could not find the id for the meeting docs folder {meeting_docs_folder}"
                    )

            print(f"Meeting Docs folder Item Id: {meeting_docs_folder_item_id}")

            ma_agenda_template_item = self._search_item_with_name(
                drive.id, self._agenda_template_excel
            )
            if ma_agenda_template_item is not None:
                ma_agenda_template_item_id = ma_agenda_template_item['id']
            print(f"NHTM Agenda Template Excel Item Id: {ma_agenda_template_item_id}")
            retry = 0
            while True:
                next_meeting_agenda_excel_item = self._search_item_with_name(
                    drive.id, self._next_tuesday_meeting_agenda_excel
                )
                if next_meeting_agenda_excel_item is not None:
                    next_meeting_agenda_excel_item_id = next_meeting_agenda_excel_item["id"]
                    next_meeting_agenda_excel_item_url = next_meeting_agenda_excel_item[
                        "webUrl"
                    ]
                    if next_meeting_agenda_excel_item_id is not None:
                        break
                if retry == 0:
                    next_meeting_agenda_excel_item_id = (
                        self._copy_agenda_to_meeting_folder(
                            graph_client,
                            drive.id,
                            ma_agenda_template_item_id,
                            meeting_docs_folder_item_id,
                            self._next_tuesday_meeting_agenda_excel,
                        )
                    )
                retry = retry + 1
                if retry < 30:
                    time.sleep(30)
                else:
                    raise AgendaException(
                        f"Could not find the id for the next meeting agenda excel {self._next_tuesday_meeting_agenda_excel}"
                    )

            print(
                f"Next Tuesday Meeting Agenda Excel Item Id: {next_meeting_agenda_excel_item_id}"
            )

            agenda_worksheet_id = self._get_agenda_worksheet_id(
                graph_client, drive.id, next_meeting_agenda_excel_item_id
            )
            print(f"Updating Agenda worksheet: {agenda_worksheet_id}")
            for group_id in group_ids:
                plan = self._get_next_meeting_plan(graph_client, group_id)
                if plan is None:
                    print(
                        f"No matching plan found for next the meeting next week in group {group_id}"
                    )
                    continue
                bucket = self._get_next_meeting_bucket(graph_client, plan)
                if bucket is None:
                    print("No matching bucket found for next the meeting next week")
                    exit(1)
                tasks = self._get_next_meeting_tasks(graph_client, bucket)
                if tasks is None:
                    print("No matching tasks found for next the meeting next week")
                    exit(1)
                meeting_assignments: dict = {}
                speakers_upn: list = []
                topics_master_upn: str = None
                for task in tasks.value:
                    assigned_to_user = self._get_assigned_to_user(graph_client, task)
                    if assigned_to_user is not None:
                        print(
                            f"{task.title}, due {task.due_date_time} is assigned to {assigned_to_user.display_name}"
                        )
                        meeting_assignments[
                            task.title.strip()
                        ] = assigned_to_user.display_name
                        if "Speaker" in task.title:
                            speakers_upn.append(assigned_to_user.user_principal_name)
                        if "Topics Master" in task.title:
                            topics_master_upn = assigned_to_user.user_principal_name
                meeting_assignments["Meeting Day"] = "Tuesday"
                meeting_assignments["Meeting Date"] = self._next_tuesday_date_us
                range_assignments: RangeAssignments = RangeAssignments()
                if self._is_next_meeting_reverse:
                    range_assignments = RangeAssignmentsReverse()
                range_assignments_map: dict = range_assignments.populate_values(
                    meeting_assignments
                )
                print(range_assignments_map)
                self._populate_agenda_worksheet(
                    drive.id,
                    next_meeting_agenda_excel_item_id,
                    agenda_worksheet_id,
                    range_assignments_map,
                )
                print(
                    f"Successfully created the agenda for the next meeting on {self._next_tuesday_date}"
                )
                # meeting_message: WeeklyMeetingMessage = WeeklyMeetingMessage(self._next_tuesday_date,
                #                                                              'Tuesday',
                #                                                              speakers_upn,
                #                                                              topics_master_upn,
                #                                                              meeting_docs_folder_item_url,
                #                                                              next_meeting_agenda_excel_item_url)
                # channel = self._get_teams_channel(graph_client, group_id, 'Weekly Meeting Channel')
                # if channel is not None:
                #     message = self._post_message_to_channel(graph_client, group_id, channel.id, meeting_message.message, meeting_message.subject, next_meeting_agenda_excel_item_url)
                #     if message is not None:
                #         print(
                #             f"Successfully posted message to the teams, 'Weekly Meeting Channel' channel."
                #         )
                return
        except RuntimeError as e:
            print(f"Error creating agenda. {e}")

        print("No matching plan or buckets were found for next the meeting next week")
        exit(1)

    @property
    def _next_tuesday(self):
        """Return the date time for next Tuesday"""
        today = datetime.date.today()
        next_tuesday = today + datetime.timedelta((1 - today.weekday()) % 7)
        return next_tuesday

    @property
    def _next_tuesday_date(self):
        """Return the date in yyyyMMdd format for next Tuesday"""
        return self._next_tuesday.strftime("%Y%m%d")

    @property
    def _next_tuesday_date_us(self):
        """Return the date in MM/dd/yyyy US format for next Tuesday"""
        return self._next_tuesday.strftime("%m/%d/%Y")

    @property
    def _next_tuesday_month(self):
        """Return the month string for next Tuesday"""
        return self._next_tuesday.strftime("%B")

    @property
    def _next_tuesday_meeting_docs(self):
        """Return the meeting docs folder name for next Tuesday"""
        return self._next_tuesday.strftime("%Y-%m-%d Meeting Docs")

    @property
    def _next_tuesday_meeting_agenda_excel(self):
        """Return the meeting agenda excel file name for next Tuesday"""
        return self._next_tuesday.strftime("NHTM Online Agenda %m-%d-%Y.xlsx")

    @property
    def _agenda_template_excel(self):
        """Return the name of the meeting agenda template excel file name"""
        agenda_template_file_name: str = self._next_tuesday.strftime(
            "NHTM Online Agenda Template %Y.xlsx"
        )
        if self._is_next_meeting_reverse:
            agenda_template_file_name = self._next_tuesday.strftime(
                "NHTM Online Agenda Reverse Template %Y.xlsx"
            )
        return agenda_template_file_name

    @property
    def _is_next_meeting_reverse(self):
        """Return if the next meeting is a reverse meeting"""
        if os.environ["REVERSE_MEETING"] is not None:
            return True
        return False

agenda_creator: AgendaCreator = AgendaCreator()
agenda_creator.create()
