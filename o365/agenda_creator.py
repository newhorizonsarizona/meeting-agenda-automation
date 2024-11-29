import asyncio
from datetime import datetime
import time
import sys
from loguru import logger
from msgraph.generated.models.planner_task import PlannerTask
from msgraph.generated.models.planner_assignments import PlannerAssignments
from o365.agenda_excel import AgendaExcel
from o365.util.constants import Constants
from o365.util.meeting_util import MeetingUtil
from o365.util.date_util import DateUtil
from o365.auth.auth_helper import AuthHelper
from o365.drive.drive_helper import DriveHelper
from o365.excel.range_assignments import RangeAssignments
from o365.excel.range_assignments_reverse import RangeAssignmentsReverse
from o365.exception.agenda_exception import AgendaException
from o365.user.user_helper import UserHelper
from o365.planner.planner_helper import PlannerHelper
from o365.graph.graph_helper import GraphHelper


class AgendaCreator:
    """This class is used for creating the agenda"""

    _group_id: str = None
    _graph_client = None
    _next_tuesday: datetime
    _next_tuesday_date: str
    _next_tuesday_date_us: str
    _next_tuesday_month: str
    _next_tuesday_meeting_docs: str
    _meeting_agenda_excel: str
    _agenda_template_excel: str
    _is_next_meeting_reverse: bool
    _meeting_util: MeetingUtil

    def __init__(self, today_date: str = None) -> None:
        """initialize the agenda creator"""
        self._group_id: str = Constants.GROUP_IDS[0]
        self._graph_client = AuthHelper.graph_service_client_with_adapter()
        date_util: DateUtil = DateUtil(today_date)
        self._next_tuesday = date_util.next_tuesday
        self._next_tuesday_date = date_util.next_tuesday_date
        self._next_tuesday_date_us = date_util.next_tuesday_date_us
        self._next_tuesday_month = date_util.next_tuesday_month
        self._meeting_util = MeetingUtil(self._next_tuesday)
        self._next_tuesday_meeting_docs = self._meeting_util.next_tuesday_meeting_docs
        self._meeting_agenda_excel = self._meeting_util.next_tuesday_agenda_excel
        self._agenda_template_excel = self._meeting_util.agenda_template_excel
        self._is_next_meeting_reverse = self._meeting_util.is_next_meeting_reverse

    def get_assigned_to_user(self, task):
        """Gets assigned to user for task"""
        retry_count = 0
        assigned_to_user = None
        while retry_count < 5:
            try:
                logger.debug(f"Getting the assigned to user for task: {task.title}")
                assigned_to_users = list(task.assignments.additional_data.keys())
                if assigned_to_users is not None and len(assigned_to_users) > 0:
                    assigned_to_user_id = list(task.assignments.additional_data.keys())[0]
                    user = asyncio.run(UserHelper.get_user(self._graph_client, assigned_to_user_id))
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
                        logger.error(f"Error getting assigned user. {e}")
                        break  # do something here, like log the error
        return assigned_to_user

    def get_drive(self):
        """Gets the drive for the specified group_id"""
        retry_count = 0
        drive_4_group = None
        while retry_count < 3:
            try:
                logger.debug(f"Getting the drive for group: {self._group_id}")
                drive = asyncio.run(DriveHelper.get_drive(self._graph_client, self._group_id))
                if drive:
                    return drive
            except RuntimeError as e:
                if "Event loop is closed" in str(e):
                    if retry_count < 5:
                        retry_count = retry_count + 1
                        time.sleep(10)
                    else:
                        logger.error(f"Error getting drive. {e}")
                        break  # do something here, like log the error
        return drive_4_group

    def _create_weekly_meeting_docs(self, drive_id, item_id, meeting_docs_folder):
        """Create the weekly meeting docs folder"""
        retry_count = 0
        folder_item_id = None
        while retry_count < 5:
            try:
                logger.debug(f"Creating the folder {meeting_docs_folder} for drive item: {item_id}")
                folder_item = asyncio.run(
                    DriveHelper.create_folder(self._graph_client, drive_id, item_id, meeting_docs_folder)
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
    def search_item_with_name(self, drive_id: str, item_name: str, parent_sub_path: str = None):
        """Search the the drive id for matching item"""
        try:
            logger.debug(f"Searching the item matching {item_name} in drive {drive_id}")
            graph_helper: GraphHelper = GraphHelper()
            if parent_sub_path is not None:
                item = graph_helper.get_request(
                    f"/drives/{drive_id}/root:/{parent_sub_path}/{item_name}?$select=name,id,webUrl",
                    {"Content-Type": "application/json"},
                )
                if item and item is not None:
                    logger.debug(f"Found {item}")
                    return item
            item = graph_helper.get_request(
                f"/drives/{drive_id}/root/search(q='{item_name}')?$select=name,id,webUrl",
                {"Content-Type": "application/json"},
            )
            if item and item["value"] is not None:
                logger.debug(f"Found item vaue {len(item['value'])}")
                for value in item["value"]:
                    if value["name"] == item_name:
                        logger.debug(f"Found item {value['name']}")
                        return value
        except AgendaException as e:
            logger.error(f"Error searching drive item {item_name}. {e}")
        return None

    # POST /drives/{drive-id}/items/{item-id}/copy'
    def _copy_agenda_to_meeting_folder(
        self,
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
                logger.debug(
                    f"Copying the agenda template {template_item_id} to meeting folder: {meeting_folder_item_id}"
                )
                copy_status = asyncio.run(
                    DriveHelper.copy_item(
                        self._graph_client,
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

    def _do_next_meeting_docs_item(
        self,
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
                self._create_weekly_meeting_docs(drive_id, wmc_drive_item_id, meeting_docs_folder)
            retry = retry + 1
            if retry < 30:
                time.sleep(30)
            else:
                raise AgendaException(f"Could not find the id for the meeting docs folder {meeting_docs_folder}")

    def _do_next_meeting_agenda_excel_item_id(
        self, drive_id, meeting_docs_folder_item_id, ma_agenda_template_item_id=None
    ):
        """Search and/or copy the next meeting agenda excel file and returns the item"""
        retry = 0
        while True:
            next_meeting_agenda_excel_item = self.search_item_with_name(drive_id, self._meeting_agenda_excel)
            if next_meeting_agenda_excel_item is not None:
                return next_meeting_agenda_excel_item
            if ma_agenda_template_item_id is not None and retry == 0:
                self._copy_agenda_to_meeting_folder(
                    drive_id,
                    ma_agenda_template_item_id,
                    meeting_docs_folder_item_id,
                    self._meeting_agenda_excel,
                )
            retry = retry + 1
            if retry < 50:
                time.sleep(30)
            else:
                raise AgendaException(
                    f"Could not find the id for the next meeting agenda excel {self._meeting_agenda_excel}"
                )

    def _get_meeting_docs_folder_item(self, drive):
        """Get the meeting docs folder item"""
        meeting_docs_folder = self._next_tuesday_meeting_docs
        wmc_drive_item = self.search_item_with_name(drive.id, "", "Weekly Meeting Channel")
        wmc_drive_item_id = wmc_drive_item["id"]
        logger.debug(f"Weekly Meeting Channel Drive Item Id: {wmc_drive_item_id}")

        meeting_docs_folder_item = self._do_next_meeting_docs_item(
            drive.id, wmc_drive_item_id, meeting_docs_folder, True
        )
        return meeting_docs_folder_item

    def _get_next_meeting_agenda_excel_item(self, drive, meeting_docs_folder_item_id, ma_agenda_template_item_id=None):
        """Get the next meeting agenda excel item"""
        next_meeting_agenda_excel_item = self._do_next_meeting_agenda_excel_item_id(
            drive.id, meeting_docs_folder_item_id, ma_agenda_template_item_id
        )
        return next_meeting_agenda_excel_item

    def prepare_drive(self, drive):
        """Prepares the drive for the next meeting"""
        try:
            logger.info(f"Preparing the meeting docs folder on drive: {drive.id}")
            meeting_docs_folder_item_id = self._get_meeting_docs_folder_item(drive)["id"]
            logger.debug(f"Meeting Docs folder Item Id: {meeting_docs_folder_item_id}")

            logger.debug("Copying the meeting agenda to meeting docs folder.")
            ma_agenda_template_item = self.search_item_with_name(
                drive.id, self._agenda_template_excel, "Meeting Automation"
            )
            if ma_agenda_template_item is None:
                raise AgendaException(f"Agenda template `{self._agenda_template_excel}` not found.")
            ma_agenda_template_item_id = ma_agenda_template_item["id"]
            logger.debug(f"NHTM Agenda Template Excel Item Id: {ma_agenda_template_item_id}")

            next_meeting_agenda_excel_item_id = self._get_next_meeting_agenda_excel_item(
                drive, meeting_docs_folder_item_id, ma_agenda_template_item_id
            )["id"]
            logger.debug(f"Next Tuesday Meeting Agenda Excel Item Id: {next_meeting_agenda_excel_item_id}")
            return next_meeting_agenda_excel_item_id
        except RuntimeError as re:
            raise AgendaException(f"An unexpected error occurred while creating meeting docs folder/ agenda file. {re}")

    def get_meeting_assignments(self):
        """Get the meeting assignments from the planner project for the month"""
        try:
            logger.info("Getting the meeting assignments from the planner project.")
            plan = PlannerHelper.get_plan_by_name(
                self._graph_client, self._group_id, self._next_tuesday_month[:3].lower()
            )
            if plan is None:
                raise AgendaException(f"No matching plan found next week in group {self._group_id}")
            bucket = PlannerHelper.get_bucket_by_name(
                self._graph_client, plan.id, f"{self._next_tuesday_date} Meeting Roles"
            )
            if bucket is None:
                raise AgendaException(f"No matching bucket found for next week in plan {plan.id}")
            tasks = self._fetch_tasks_in_bucket(bucket.id)
            if tasks is None:
                raise AgendaException("No matching tasks found for next the meeting next week")
            meeting_assignments: dict = {}
            for task in tasks:
                assigned_to_user = self.get_assigned_to_user(task)
                if assigned_to_user is not None:
                    logger.debug(
                        f"{task.title}, due {task.due_date_time} is assigned to {assigned_to_user.display_name}"
                    )
                    meeting_assignments[task.title.strip()] = assigned_to_user.display_name
            meeting_assignments["Meeting Day"] = "Tuesday"
            meeting_assignments["Meeting Date"] = self._next_tuesday_date_us
            return meeting_assignments
        except Exception as e:
            raise AgendaException(f"An unexpected error occurred while getting the meeting assignments. {e}")

    # GET https://graph.microsoft.com/v1.0/planner/buckets/{bucket-id}/tasks
    def _fetch_tasks_in_bucket(self, bucket_id):
        """Fetches the tasks in a planner bucket with specified id"""
        try:
            logger.debug(f"Fetching the planner tasks from buucket {bucket_id}")
            graph_helper: GraphHelper = GraphHelper()
            tasks = graph_helper.get_request(
                f"planner/buckets/{bucket_id}/tasks",
                {"Content-Type": "application/json"},
            )
            if tasks and tasks["value"] is not None:
                logger.debug(f"Found {len(tasks['value'])} tasks in bucket {bucket_id}.")
                planner_tasks = []
                for task in tasks["value"]:
                    planner_task = PlannerTask()
                    planner_task.id = task["id"]
                    planner_task.title = task["title"]
                    planner_task.percent_complete = task["percentComplete"]
                    planner_task.priority = task["priority"]
                    if task["dueDateTime"] is not None:
                        planner_task.due_date_time = datetime.strptime(task["dueDateTime"], "%Y-%m-%dT%H:%M:%SZ")
                    if task["assignments"] is not None:
                        planner_task.assignments = PlannerAssignments(additional_data=task["assignments"])
                    planner_tasks.append(planner_task)
                logger.debug(f"Tasks: {planner_tasks}")
                return planner_tasks
        except AgendaException as e:
            logger.error(f"Error getting tasks from bucket { {bucket_id}}. {e}")
        return None

    def populate_agenda_worksheet(self, drive, next_meeting_agenda_excel_item_id: str, meeting_assignments: dict):
        """Populate the meeting assignments in the agenda excel worksheet"""
        try:
            logger.debug("Populating the agenda excel worksheet with the assignments")
            range_assignments: RangeAssignments = (
                RangeAssignments() if not self._is_next_meeting_reverse else RangeAssignmentsReverse()
            )
            range_assignments_map: dict = range_assignments.populate_values(meeting_assignments)
            logger.debug(range_assignments_map)
            agenda_excel = AgendaExcel(drive.id, next_meeting_agenda_excel_item_id, self._is_next_meeting_reverse)
            agenda_worksheet_id = agenda_excel.populate(range_assignments_map)
            logger.debug(f"Updated Agenda worksheet: {agenda_worksheet_id}")
            return agenda_worksheet_id
        except RuntimeError as re:
            raise AgendaException(f"An unexpected error occurred while populating the agenda excel worksheet. {re}")

    def create(self):
        """Get the planner tasks for next meeting"""
        logger.info("Checking if the meeting docs folder and agenda exist")
        try:
            if self._next_tuesday in DateUtil().get_last_two_tuesdays_of_year():
                logger.info("Skip creating the agenda as we are having a break on {self._next_tuesday_date_us}")
                return
            drive = self.get_drive()
            logger.debug(f"Drive id: {drive.id}")
            next_meeting_agenda_excel_item_id = self.prepare_drive(drive)
            meeting_assignments: dict = self.get_meeting_assignments()
            self.populate_agenda_worksheet(drive, next_meeting_agenda_excel_item_id, meeting_assignments)

            logger.info(f"Successfully created the agenda for the next meeting on {self._next_tuesday_date}")
            return "Success"
        except AgendaException as ae:
            logger.error(f"An exception has occurred. {ae}")
        except RuntimeError as e:
            logger.critical(f"Unexpected error has occurred. {e}")

        logger.error("No matching plan or buckets were found for next the meeting next week")
        sys.exit(1)
