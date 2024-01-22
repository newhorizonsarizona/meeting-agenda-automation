import json
import time
from o365.agenda_creator import AgendaCreator
from o365.auth.auth_helper import AuthHelper
from o365.excel.excel_helper import ExcelHelper
from o365.excel.range_assignments import RangeAssignments
from o365.excel.range_assignments_reverse import RangeAssignmentsReverse
from o365.exception.agenda_exception import AgendaException
from o365.graph.graph_helper import GraphHelper
from o365.teams.weekly_meeting_message import WeeklyMeetingMessage
from o365.user.user_helper import UserHelper
from o365.util.constants import Constants
from o365.planner.planner_helper import PlannerHelper
from o365.teams.teams_helper import TeamsHelper


class AgendaNotifier(AgendaCreator):
    """This class is used for sending the agenda notifications"""

    def __init__(self, today_date: str = None) -> None:
        """initialize the agenda notifier"""
        super().__init__(today_date)

    # GET /drives/{drive-id}/items/{id}/workbook/worksheets/{id|name}/range(address='A1:B2')?$select=values
    def _get_range_values(self, drive_id: str, item_id: str, worksheet_id: str, range_address: str):
        """Search the the drive id for matching item"""
        try:
            print(f"Getting the range values for item matching {item_id} for range address {range_address}")
            graph_helper: GraphHelper = GraphHelper()
            range_values = graph_helper.get_request(
                f"/drives/{drive_id}/items/{item_id}/workbook/worksheets/{worksheet_id}/range(address='{range_address}')?$select=values",
                {"Content-Type": "application/json"},
            )
            if range_values and range_values is not None:
                print(range_values["values"])
                return range_values["values"]
        except Exception as e:
            print(f"Error: {e}")
        return None

    # GET /users?$filter=startswith(displayName,'a')&$orderby=displayName&$count=true&$top=1
    def _get_user_by_display_name(self, display_name: str):
        """Get the users with display name that matches"""
        try:
            print(f"Getting the users that matches the name {display_name}")
            graph_helper: GraphHelper = GraphHelper()
            users = graph_helper.get_request(
                f"/users?$filter=startswith(displayName,'{display_name.replace(' ','%20')}')&$count=true&$top=1&$select=id,displayName",
                {"Content-Type": "application/json"},
            )
            if users and users["value"] is not None:
                print(users["value"])
                return users["value"]
        except Exception as e:
            print(f"Error: {e}")
        return None

    # GET /teams/{team-id}/channels?$filter=startswith(displayName,'a')&$select=id,displayName
    def _get_teams_channel_by_display_name(self, team_id: str, display_name: str):
        """Get the users with display name that matches"""
        try:
            print(f"Getting the teams channel that matches the {display_name}")
            graph_helper: GraphHelper = GraphHelper()
            channels = graph_helper.get_request(
                f"/teams/{team_id}/channels?$filter=startswith(displayName,'{display_name.replace(' ','%20')}')&$select=id,displayName",
                {"Content-Type": "application/json"},
            )
            if channels and channels["value"] is not None:
                print(channels["value"])
                return channels["value"]
        except Exception as e:
            print(f"Error: {e}")
        return None

    # POST /teams/{team-id}/channels/{channel-id}/messages
    def _post_message_to_channel(self, team_id: str, channel_id: str, chat_message: dict):
        """Post chat message to specified channel in team"""
        try:
            print(f"Posting message to teams channel that matches the id {channel_id}")
            graph_helper: GraphHelper = GraphHelper(True)
            messages = graph_helper.post_request(
                f"/teams/{team_id}/channels/{channel_id}/messages",
                json.dumps(chat_message, indent=None),
                {"Content-Type": "application/json"},
            )
            if messages and messages["id"] is not None:
                print(messages["id"])
                return messages["id"]
        except Exception as e:
            print(f"Error: {e}")
        return None

    def send(self):
        """Send the agenda notification on teams"""
        print("Preparing agenda notification")
        try:
            graph_client = AuthHelper.graph_service_client_with_adapter()
            group_id = Constants.GROUP_IDS[0]
            drive = self.get_drive(graph_client, group_id)
            print(f"Drive id: {drive.id}")
            meeting_docs_folder = self._next_tuesday_meeting_docs
            wmc_drive_item = self.search_item_with_name(drive.id, "Weekly Meeting Channel")
            wmc_drive_item_id = wmc_drive_item["id"]
            print(f"Weekly Meeting Channel Drive Item Id: {wmc_drive_item_id}")

            meeting_docs_folder_item = self._do_next_meeting_docs_item_id(
                graph_client, drive.id, wmc_drive_item_id, meeting_docs_folder, False
            )
            meeting_docs_folder_item_id = meeting_docs_folder_item["id"]
            print(f"Meeting Docs folder Item Id: {meeting_docs_folder_item_id}")

            next_meeting_agenda_excel_item = self._do_next_meeting_agenda_excel_item_id(
                graph_client, drive.id, None, meeting_docs_folder_item_id, False
            )
            next_meeting_agenda_excel_item_id = next_meeting_agenda_excel_item["id"]
            print(f"Next Tuesday Meeting Agenda Excel Item Id: {next_meeting_agenda_excel_item_id}")
            agenda_worksheet_id = self._get_agenda_worksheet_id(
                graph_client, drive.id, next_meeting_agenda_excel_item_id
            )
            print(f"Getting functionaries from Agenda worksheet: {agenda_worksheet_id}")

            speakers: list = []
            topics_master = None
            range_assignments: RangeAssignments = (
                RangeAssignments() if not self._is_next_meeting_reverse else RangeAssignmentsReverse()
            )
            range_assignments_map: dict = range_assignments.range_assignments_map
            for range_assignment_value_map in range_assignments_map.values():
                range_column: str = "G"
                range_row: int = 5
                for range_assignment_value_row_values in range_assignment_value_map["names"]:
                    for range_assignment_value_col_value in range_assignment_value_row_values:
                        if range_assignment_value_col_value is None:
                            continue
                        range_values = self._get_range_values(
                            drive.id,
                            next_meeting_agenda_excel_item_id,
                            agenda_worksheet_id,
                            f"{range_column}{range_row}",
                        )
                        if range_values:
                            if "Speaker" in range_assignment_value_col_value and range_values[0][0] != "":
                                speaker_user = self._get_user_by_display_name(range_values[0][0])
                                if speaker_user is not None:
                                    speakers.append(speaker_user[0])
                            elif "Topics Master" in range_assignment_value_col_value:
                                topics_master_user = self._get_user_by_display_name(range_values[0][0])
                                if topics_master_user is not None:
                                    topics_master = topics_master_user[0]
                    range_row += 1

            print(f"Successfully fetched assignments from the agenda for the next meeting on {self._next_tuesday_date}")
            print(f"Speakers: {speakers}, Topics Master: {topics_master}")
            meeting_message: WeeklyMeetingMessage = WeeklyMeetingMessage(
                self._next_tuesday_date,
                "Tuesday",
                speakers,
                topics_master,
                meeting_docs_folder_item,
                next_meeting_agenda_excel_item,
            )
            teams_helper: TeamsHelper = TeamsHelper()
            channel = self._get_teams_channel_by_display_name(group_id, "Weekly Meeting Channel")
            chat_message = TeamsHelper.generate_chat_message_dict(meeting_message)
            print(chat_message)
            if channel is not None and chat_message is not None:
                message = self._post_message_to_channel(group_id, channel[0]["id"], chat_message)
                if message is not None:
                    print(f"Successfully posted message to the teams, 'Weekly Meeting Channel' channel.")
            return
        except RuntimeError as e:
            print(f"Error sending agenda notification. {e}")

        print("No matching plan or buckets were found for next the meeting next week")
        exit(1)

    def create_and_send(self):
        """Create the next meeting agenda and send the notification on teams"""
        self.create()
        self.send()
