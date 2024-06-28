import json
import sys
from loguru import logger
from o365.agenda_creator import AgendaCreator
from o365.excel.range_assignments import RangeAssignments
from o365.excel.range_assignments_reverse import RangeAssignmentsReverse
from o365.exception.agenda_exception import AgendaException
from o365.graph.graph_helper import GraphHelper
from o365.teams.weekly_meeting_message import WeeklyMeetingMessage
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
            logger.debug(f"Getting the range values for item matching {item_id} for range address {range_address}")
            graph_helper: GraphHelper = GraphHelper()
            range_values = graph_helper.get_request(
                f"/drives/{drive_id}/items/{item_id}/workbook/worksheets/{worksheet_id}/range(address='{range_address}')?$select=values",
                {"Content-Type": "application/json"},
            )
            if range_values and range_values is not None:
                logger.debug(range_values["values"])
                return range_values["values"]
        except AgendaException as e:
            logger.error(f"Error gettng range values: {e}")
        return None

    # GET /users?$filter=startswith(displayName,'a')&$orderby=displayName&$count=true&$top=1
    def _get_user_by_display_name(self, display_name: str):
        """Get the users with display name that matches"""
        try:
            logger.debug(f"Getting the users that matches the name {display_name}")
            graph_helper: GraphHelper = GraphHelper()
            users = graph_helper.get_request(
                f"/users?$filter=startswith(displayName,'{display_name.replace(' ','%20')}')&$count=true&$top=1&$select=id,displayName",
                {"Content-Type": "application/json"},
            )
            if users and users["value"] is not None:
                logger.debug(users["value"])
                return users["value"]
        except AgendaException as e:
            logger.error(f"Error getting user display name: {e}")
        return None

    # GET /teams/{team-id}/channels?$filter=startswith(displayName,'a')&$select=id,displayName
    def _get_teams_channel_by_display_name(self, team_id: str, display_name: str):
        """Get the users with display name that matches"""
        try:
            logger.debug(f"Getting the teams channel that matches the {display_name}")
            graph_helper: GraphHelper = GraphHelper()
            channels = graph_helper.get_request(
                f"/teams/{team_id}/channels?$filter=startswith(displayName,'{display_name.replace(' ','%20')}')&$select=id,displayName",
                {"Content-Type": "application/json"},
            )
            if channels and channels["value"] is not None:
                logger.debug(channels["value"])
                return channels["value"]
        except AgendaException as e:
            logger.error(f"Error getting channel display name: {e}")
        return None

    # POST /teams/{team-id}/channels/{channel-id}/messages
    def _post_message_to_channel(self, team_id: str, channel_id: str, chat_message: dict):
        """Post chat message to specified channel in team"""
        try:
            logger.debug(f"Posting message to teams channel that matches the id {channel_id}")
            graph_helper: GraphHelper = GraphHelper(True)
            messages = graph_helper.post_request(
                f"/teams/{team_id}/channels/{channel_id}/messages",
                json.dumps(chat_message, indent=None),
                {"Content-Type": "application/json"},
            )
            if messages and messages["id"] is not None:
                logger.debug(messages["id"])
                return messages["id"]
        except AgendaException as e:
            logger.error(f"Error posting message to teams: {e}")
        return None

    # PATCH /teams/(team-id)/channels/{channel-id}/messages/{message-id}
    def _update_message_on_channel(self, team_id: str, channel_id: str, message_id: str, chat_message: dict):
        """Update chat message on specified channel in team"""
        try:
            logger.debug(
                f"Updating message on teams channel that matches the id {channel_id} and message id {message_id}"
            )
            graph_helper: GraphHelper = GraphHelper(True)
            messages = graph_helper.patch_request(
                f"/teams/{team_id}/channels/{channel_id}/messages/{message_id}",
                json.dumps(chat_message, indent=None),
                {"Content-Type": "application/json"},
            )
            if messages and messages["id"] is not None:
                logger.debug(messages["id"])
                return messages["id"]
        except AgendaException as e:
            logger.error(f"Error updating message on teams: {e}")
        return None

    # POST https://newhorizonsarizonaorg.webhook.office.com/webhookb2/..
    def _post_message_to_channel_webhook(self, message_adaptive_card: dict):
        """Post the message on teams channel webhook url"""
        try:
            logger.debug("Posting message on teams channel webhook")
            graph_helper: GraphHelper = GraphHelper()
            headers = {"Content-Type": "application/json"}
            result = graph_helper.post_request_to_url(
                self._meeting_util.teams_webhook_url, json.dumps(message_adaptive_card), headers
            )
            if result:
                logger.debug("Message was posted to the teams channel webhook successfully")
        except AgendaException as e:
            logger.error(f"Error posting message to the teams channel webhook: {e}")

    def send(self):
        """Send the agenda notification on teams"""
        logger.info("Preparing agenda notification")
        try:
            drive = self.get_drive()
            logger.debug(f"Drive id: {drive.id}")
            meeting_docs_folder_item = self._get_meeting_docs_folder_item(drive)
            next_meeting_agenda_excel_item = self._get_next_meeting_agenda_excel_item(
                drive, meeting_docs_folder_item["id"]
            )
            next_meeting_agenda_excel_item_id = next_meeting_agenda_excel_item["id"]
            agenda_worksheet_id = self._get_agenda_worksheet_id(drive.id, next_meeting_agenda_excel_item_id)
            logger.debug(f"Getting functionaries from Agenda worksheet: {agenda_worksheet_id}")

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
                        if range_values is None:
                            continue
                        if "Speaker" in range_assignment_value_col_value and range_values[0][0] != "":
                            speaker_user = self._get_user_by_display_name(range_values[0][0])
                            if speaker_user is not None:
                                speakers.append(speaker_user[0])
                        elif "Topics Master" in range_assignment_value_col_value:
                            topics_master_user = self._get_user_by_display_name(range_values[0][0])
                            if topics_master_user is not None:
                                topics_master = topics_master_user[0]
                    range_row += 1

            logger.info(
                f"Successfully fetched assignments from the agenda for the next meeting on {self._next_tuesday_date}"
            )
            logger.debug(f"Speakers: {speakers}, Topics Master: {topics_master}")
            meeting_message: WeeklyMeetingMessage = WeeklyMeetingMessage(
                self._next_tuesday_date,
                "Tuesday",
                speakers,
                topics_master,
                meeting_docs_folder_item,
                next_meeting_agenda_excel_item,
            )
            if self._meeting_util.teams_webhook_url is not None:
                self._post_message_to_channel_webhook(meeting_message.adaptive_card_message)
                return
            channel = self._get_teams_channel_by_display_name(self._group_id, "Weekly Meeting Channel")
            chat_message = TeamsHelper.generate_chat_message_dict(meeting_message)
            if channel is not None and chat_message is not None:
                current_message = TeamsHelper.find_message_in_channel(
                    self._graph_client, self._group_id, channel[0]["id"], meeting_message
                )
                if current_message is not None:
                    current_message_id = self._update_message_on_channel(
                        self._group_id, channel[0]["id"], current_message.id, chat_message
                    )
                    if current_message_id is not None:
                        logger.info("Successfully updated message on the teams, 'Weekly Meeting Channel' channel.")
                        return
                message_id = self._post_message_to_channel(self._group_id, channel[0]["id"], chat_message)
                if message_id is not None:
                    logger.info("Successfully posted message to the teams, 'Weekly Meeting Channel' channel.")
            return
        except RuntimeError as e:
            logger.critical(f"Unexpected error sending agenda notification. {e}")

        logger.error("No matching plan or buckets were found for next the meeting next week")
        sys.exit(1)

    def create_and_send(self):
        """Create the next meeting agenda and send the notification on teams"""
        self.create()
        self.send()
