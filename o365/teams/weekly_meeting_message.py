class WeeklyMeetingMessage:
    """This class is used for storing the weekly meeting message"""

    _subject: str = "{meeting_date} - WEEKLY MEETING"
    _title: str = "WEEKLY MEETING @ Cadence Living in Chandler, 100 W Queen Creek Rd., Chandler, AZ 85248"
    _salutation: str = "Dear New Horizons Toastmasters Club members,"
    _message_part1: str = (
        "Please find attached the agenda for the {meeting_day}, {meeting_date} meeting. \
                This is going to be a hybrid meeting. Guests are welcome."
    )
    _message_part2: str = (
        "{speakers_display_names} please place your speech introduction(s) and evaluation forms in the meeting folder. \
                {topics_master_display_name} please post the  meeting theme here."
    )
    _message_part3: str = "_Meeting Folder:_ {meeting_folder_url}"
    _message_part4: str = "_Agenda:_ {meeting_agenda_url}"
    _message_reminders: str = "REMINDERS: Please mute your phones"
    _message_footer1: str = "Best Regards,"
    _message_footer2: str = "NHTM Education Committee"
    _message: str = (
        " \
        {meeting_date} {title}<br/> \
        {attachments}<div>{salutation}<br/><br/> \
            {message_part1}<br/> \
            {speakers_mention} please place your speech introduction(s) and evaluation forms in the meeting folder. \
                {topics_master_mention} please post the  meeting theme here.<br/><br/> \
            <u>Meeting Folder:</u> {meeting_folder_url}<br/> \
            <u>Agenda:</u> {meeting_agenda_url}<br/> \
            {message_reminders}<br/><br/> \
        {message_footer1},<br/> \
        {message_footer2}<br/></div>"
    )
    speaker_users: list = []
    topics_master_user = None
    meeting_agenda_item = None
    meeting_folder_item = None
    attachment_content_type: str = "application/vnd.ms-excel"

    def __init__(
        self,
        meeting_date,
        meeting_day,
        speaker_users,
        topics_master_user,
        meeting_folder_item,
        meeting_agenda_item,
    ) -> None:
        """initialize the message assignments"""
        self._subject = self._subject.format(meeting_date=meeting_date)
        self.speaker_users = speaker_users
        self.topics_master_user = topics_master_user
        self.meeting_agenda_item = meeting_agenda_item
        self.meeting_folder_item = meeting_folder_item
        speakers_mention = ""
        speakers_display_names = ""
        mention_id = 0
        for speaker_user in speaker_users:
            speakers_mention += f'<at id="{mention_id}">{speaker_user["displayName"]}</at>, '
            speakers_display_names += f'{speaker_user["displayName"]}, '
            mention_id += 1
        topics_master_mention = f'<at id="{mention_id}">{topics_master_user["displayName"]}</at>'
        attachments = f'<attachment id="{meeting_agenda_item["id"]}">{meeting_agenda_item["name"]}</attachment>'
        self._message_part1 = self._message_part1.format(meeting_date=meeting_date, meeting_day=meeting_day)
        self._message_part2 = self._message_part2.format(
            speakers_display_names=speakers_display_names, topics_master_display_name=topics_master_user["displayName"]
        )
        self._message_part3 = self._message_part3.format(
            meeting_folder_url=f'[{meeting_folder_item["name"].strip()}]({meeting_folder_item["webUrl"].strip()})'
        )
        self._message_part4 = self._message_part4.format(
            meeting_agenda_url=f'[{meeting_agenda_item["name"].strip()}]({meeting_agenda_item["webUrl"].strip()})'
        )
        self._message = self._message.format(
            meeting_date=meeting_date,
            message_part1=self._message_part1,
            title=self._title,
            salutation=self._salutation,
            speakers_mention=speakers_mention,
            topics_master_mention=topics_master_mention,
            meeting_folder_url=f'<a href="{meeting_folder_item["webUrl"]}">{meeting_folder_item["name"]}</a>',
            meeting_agenda_url=f'<a href="{meeting_agenda_item["webUrl"]}">{meeting_agenda_item["name"]}</a>',
            attachments=attachments,
            message_reminders=self._message_reminders,
            message_footer1=self._message_footer1,
            message_footer2=self._message_footer2,
        )

    @property
    def subject(self) -> None:
        """get the trimmed subject"""
        return self._subject.strip().strip("\n")

    @property
    def message(self) -> None:
        """get the trimmed message"""
        return self._message.strip().strip("\n")

    @property
    def adaptive_card_message(self):
        """get the adaptive card message for notification"""
        adaptive_card_message = {
            "type": "message",
            "attachments": [
                {
                    "contentType": "application/vnd.microsoft.card.adaptive",
                    "content": {
                        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                        "type": "AdaptiveCard",
                        "version": "1.2",
                        "body": [
                            {
                                "type": "Container",
                                "items": [
                                    {
                                        "type": "TextBlock",
                                        "text": f"{self._subject}",
                                        "weight": "bolder",
                                        "size": "large",
                                        "wrap": True,
                                        "isMarkdown": True,
                                    }
                                ],
                            },
                            {
                                "type": "Container",
                                "items": [
                                    {
                                        "type": "TextBlock",
                                        "text": f"{self._title}",
                                        "weight": "bolder",
                                        "size": "medium",
                                        "wrap": True,
                                        "isMarkdown": True,
                                    },
                                    {
                                        "type": "TextBlock",
                                        "text": f"{self._salutation}",
                                        "size": "medium",
                                        "wrap": True,
                                        "isMarkdown": True,
                                    },
                                    {
                                        "type": "TextBlock",
                                        "text": f"{self._message_part1}",
                                        "size": "medium",
                                        "wrap": True,
                                        "isMarkdown": True,
                                    },
                                    {
                                        "type": "TextBlock",
                                        "text": f"{self._message_part2}",
                                        "size": "medium",
                                        "wrap": True,
                                        "isMarkdown": True,
                                    },
                                    {
                                        "type": "TextBlock",
                                        "text": f"{self._message_part3}",
                                        "size": "medium",
                                        "wrap": True,
                                        "isMarkdown": True,
                                    },
                                    {
                                        "type": "TextBlock",
                                        "text": f"{self._message_part4}",
                                        "size": "medium",
                                        "wrap": True,
                                        "isMarkdown": True,
                                    },
                                    {
                                        "type": "TextBlock",
                                        "text": f"{self._message_reminders}",
                                        "size": "medium",
                                        "weight": "bolder",
                                        "wrap": True,
                                        "isMarkdown": True,
                                    },
                                    {
                                        "type": "TextBlock",
                                        "text": f"{self._message_footer1}",
                                        "size": "medium",
                                        "wrap": True,
                                        "isMarkdown": True,
                                    },
                                    {
                                        "type": "TextBlock",
                                        "text": f"{self._message_footer2}",
                                        "size": "medium",
                                        "wrap": True,
                                        "isMarkdown": True,
                                    },
                                ],
                            },
                        ],
                    },
                }
            ],
        }
        return adaptive_card_message
