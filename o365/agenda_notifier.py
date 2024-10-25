import json
import sys
from loguru import logger
from o365.agenda_creator import AgendaCreator
from o365.agenda_excel import AgendaExcel
from o365.exception.agenda_exception import AgendaException
from o365.graph.graph_helper import GraphHelper
from o365.teams.weekly_meeting_message import WeeklyMeetingMessage
from o365.teams.teams_helper import TeamsHelper


class AgendaNotifier(AgendaCreator):
    """This class is used for sending the agenda notifications"""

    def __init__(self, today_date: str = None) -> None:
        """initialize the agenda notifier"""
        super().__init__(today_date)

    # GET /teams/{team-id}/channels?$filter=startswith(displayName,'a')&$select=id,displayName
    def _get_teams_channel_by_display_name(self, team_id: str, display_name: str):
        """Get the users with display name that matches"""
        try:
            logger.debug(f"Getting the teams channel that matches the {display_name}")
            graph_helper: GraphHelper = GraphHelper()
            channels = graph_helper.get_request(
                f"/teams/{team_id}/channels?"
                f"$filter=startswith(displayName,'{display_name.replace(' ','%20')}')&$select=id,displayName",
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
            agenda_excel = AgendaExcel(drive.id, next_meeting_agenda_excel_item["id"], self._is_next_meeting_reverse)
            logger.info(
                f"Successfully fetched assignments from the agenda for the next meeting on {self._next_tuesday_date}"
            )

            meeting_message: WeeklyMeetingMessage = WeeklyMeetingMessage(
                meeting_date=self._next_tuesday_date,
                meeting_day="Tuesday",
                speaker_users=agenda_excel.speaker_assignments,
                topics_master_user=agenda_excel.topics_master_assignment,
                meeting_folder_item=meeting_docs_folder_item,
                meeting_agenda_item=next_meeting_agenda_excel_item,
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

    def send_signup_reminder(self):
        """Send the agenda signup reminder notification on teams"""
        logger.info("Preparing agenda signup reminder notification")
        try:
            drive = self.get_drive()
            logger.debug(f"Drive id: {drive.id}")
            meeting_docs_folder_item = self._get_meeting_docs_folder_item(drive)
            next_meeting_agenda_excel_item = self._get_next_meeting_agenda_excel_item(
                drive, meeting_docs_folder_item["id"]
            )
            agenda_excel = AgendaExcel(drive.id, next_meeting_agenda_excel_item["id"], self._is_next_meeting_reverse)
            logger.info(
                f"Successfully fetched assignments from the agenda for the next meeting on {self._next_tuesday_date}"
            )

            if self._meeting_util.teams_webhook_url is not None:
                signup_reminder_card = WeeklyMeetingMessage.adaptive_card_signup_message(
                    meeting_date=self._next_tuesday_date_us,
                    meeting_day="Tuesday",
                    meeting_agenda_item=next_meeting_agenda_excel_item,
                    agenda_excel=agenda_excel,
                )
                if signup_reminder_card is None:
                    logger.info(
                        f"Awesome! No functionary roles need to be filled at this time for Tuesday, {self._next_tuesday_date}."
                    )
                    return
                logger.debug(f"Payload: {signup_reminder_card}")
                self._post_message_to_channel_webhook(signup_reminder_card)
                return

        except RuntimeError as e:
            logger.critical(f"Unexpected error sending agenda signup reminder notification. {e}")
            sys.exit(1)
