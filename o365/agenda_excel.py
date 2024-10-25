import asyncio
import json
import time
from o365.auth.auth_helper import AuthHelper
from o365.excel.excel_helper import ExcelHelper
from o365.excel.range_assignments import RangeAssignments
from o365.excel.range_assignments_reverse import RangeAssignmentsReverse
from loguru import logger
from o365.exception.agenda_exception import AgendaException
from o365.graph.graph_helper import GraphHelper


class AgendaExcel:
    """This class is used to keep the agenda excel contents"""

    _graph_client = None
    _drive_id: str
    _agenda_excel_item_id: str
    _range_assignments: RangeAssignments
    _agenda_worksheet_id: str

    def __init__(self, drive_id: str, agenda_excel_item_id: str, reverse_meeting: bool = False) -> None:
        """initialize the agenda excel"""
        self._graph_client = AuthHelper.graph_service_client_with_adapter()
        self._drive_id = drive_id
        self._agenda_excel_item_id = agenda_excel_item_id
        self._range_assignments = RangeAssignments() if not reverse_meeting else RangeAssignmentsReverse()
        self._agenda_worksheet_id = self._get_agenda_worksheet_id(drive_id, agenda_excel_item_id)

    @property
    def all_functionary_role_assignments(self) -> dict:
        """Get the functionary role assignments from the agenda excel"""
        functionary_role_assignments: dict = {}
        range_assignments_map: dict = self._range_assignments.range_assignments_map["G5:G41"]
        range_column: str = "G"
        range_row: int = 5
        for range_assignment_value_row_values in range_assignments_map["names"]:
            for range_assignment_value_col_value in range_assignment_value_row_values:
                if range_assignment_value_col_value is None:
                    continue
                range_values = self._get_range_values(
                    self._drive_id,
                    self._agenda_excel_item_id,
                    self._agenda_worksheet_id,
                    f"{range_column}{range_row}",
                )
                assigned_member = range_values[0][0]
                if assigned_member is not None:
                    assigned_member = str(assigned_member).strip()
                    if assigned_member == "0" or assigned_member == "":
                        assigned_member = None
                functionary_role_assignments[range_assignment_value_col_value] = assigned_member
            range_row += 1

        logger.debug(f"Functionary Role Assignments: {functionary_role_assignments}")
        return functionary_role_assignments

    @property
    def speaker_assignments(self) -> list:
        """Get the speaker assignments from the agenda excel"""
        speaker_assignments: list = []
        range_assignments_map: dict = self._range_assignments.range_assignments_map["G5:G41"]
        range_column: str = "G"
        range_row: int = 5
        for range_assignment_value_row_values in range_assignments_map["names"]:
            for range_assignment_value_col_value in range_assignment_value_row_values:
                if range_assignment_value_col_value is None:
                    continue
                range_values = self._get_range_values(
                    self._drive_id,
                    self._agenda_excel_item_id,
                    self._agenda_worksheet_id,
                    f"{range_column}{range_row}",
                )
                if range_values is None:
                    continue
                if "Speaker" in range_assignment_value_col_value and range_values[0][0] != "":
                    speaker_user = self._get_user_by_display_name(range_values[0][0])
                    if speaker_user is not None:
                        speaker_assignments.append(speaker_user[0])
            range_row += 1

        logger.debug(f"Speaker Assignments: {speaker_assignments}")
        return speaker_assignments

    @property
    def topics_master_assignment(self):
        """Get the topics master assignment from the agenda excel"""
        topics_master_assignment = None
        range_assignments_map: dict = self._range_assignments.range_assignments_map["G5:G41"]
        range_column: str = "G"
        range_row: int = 5
        for range_assignment_value_row_values in range_assignments_map["names"]:
            for range_assignment_value_col_value in range_assignment_value_row_values:
                if range_assignment_value_col_value is None:
                    continue
                range_values = self._get_range_values(
                    self._drive_id,
                    self._agenda_excel_item_id,
                    self._agenda_worksheet_id,
                    f"{range_column}{range_row}",
                )
                if range_values is None:
                    continue
                if "Topics Master" in range_assignment_value_col_value:
                    topics_master_user = self._get_user_by_display_name(range_values[0][0])
                    if topics_master_user is not None:
                        topics_master_assignment = topics_master_user[0]
                        break
            range_row += 1

        logger.debug(f"Topics Master Assignment: {topics_master_assignment}")
        return topics_master_assignment

    # GET /users?$filter=startswith(displayName,'a')&$orderby=displayName&$count=true&$top=1
    def _get_user_by_display_name(self, display_name: str):
        """Get the users with display name that matches"""
        try:
            logger.debug(f"Getting the users that matches the name {display_name}")
            graph_helper: GraphHelper = GraphHelper()
            users = graph_helper.get_request(
                f"/users?$filter=startswith(displayName,'{display_name.replace(' ','%20')}')"
                "&$count=true&$top=1&$select=id,displayName",
                {"Content-Type": "application/json"},
            )
            if users and users["value"] is not None:
                logger.debug(users["value"])
                return users["value"]
        except AgendaException as e:
            logger.error(f"Error getting user display name: {e}")
        return None

    # GET /drives/{drive-id}/items/{id}/workbook/worksheets/{id|name}/range(address='A1:B2')?$select=values
    def _get_range_values(self, drive_id: str, item_id: str, worksheet_id: str, range_address: str):
        """Search the the drive id for matching item"""
        try:
            logger.debug(f"Getting the range values for item matching {item_id} for range address {range_address}")
            graph_helper: GraphHelper = GraphHelper()
            range_values = graph_helper.get_request(
                f"/drives/{drive_id}/items/{item_id}/workbook/worksheets/{worksheet_id}"
                f"/range(address='{range_address}')?$select=values",
                {"Content-Type": "application/json"},
            )
            if range_values and range_values is not None:
                logger.debug(range_values["values"])
                return range_values["values"]
        except AgendaException as e:
            logger.error(f"Error gettng range values: {e}")
        return None

    # GET /drives/{drive-id}/items/{id}/workbook/worksheets/
    def _get_agenda_worksheet_id(self, drive_id, item_id):
        """Create the Agenda worksheet id"""
        retry_count = 0
        excel_worksheet_id = None
        while retry_count < 10:
            try:
                logger.debug(f"Getting the agenda worksheet id for drive item: {item_id}")
                worksheets = asyncio.run(ExcelHelper.get_worksheets(self._graph_client, drive_id, item_id))
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
            logger.debug(
                f"Updating the worksheet range {range_address} for item {item_id} \
					and worksheeet{worksheet_id} in drive {drive_id}"
            )
            graph_helper: GraphHelper = GraphHelper()
            data_json = json.dumps(range_data)
            logger.debug(data_json)
            range_update_result = graph_helper.patch_request(
                f"/drives/{drive_id}/items/{item_id}/workbook/worksheets/{worksheet_id}"
                f"/range(address='{range_address}')",
                data_json,
                {"Content-Type": "application/json"},
            )
            if range_update_result:
                logger.debug(f"Range update result {range_update_result}")
                return range_update_result
        except AgendaException as e:
            logger.error(f"Error updating worksheet range address {range_address}. {e}")
        return None

    def populate(self, range_assignments_map: dict):
        """Populating the agenda worksheet based on specified range asssignments"""
        for range_key, range_value in range_assignments_map.items():
            range_data: dict = {
                "values": range_value["values"],
                "formulas": range_value["formulas"],
                "numberFormat": range_value["formats"],
            }
            self._update_agenda_worksheet_range(
                self._drive_id, self._agenda_excel_item_id, self._agenda_worksheet_id, range_key, range_data
            )
            time.sleep(2)
        return self._agenda_worksheet_id
