class WeeklyMeetingMessage:
    """This class is used for storing the weekly meeting message"""

    _subject: str = "{meeting_date} - WEEKLY MEETING"
    _message: str = " \
        {meeting_date} WEEKLY MEETING @ Cadence Living in Chandler, 100 W Queen Creek Rd., Chandler, AZ 85248<br/> \
        {attachments}<div>Dear New Horizons Toastmasters Club members,<br/><br/> \
            Please find attached the agenda for the {meeting_day}, {meeting_date} meeting. This is going to be a hybrid meeting. Guests are welcome.<br/> \
            {speakers_mention} please place your speech introduction(s) and evaluation forms in the meeting folder. {topics_master_mention} please post the  \
            meeting theme here.<br/><br/> \
            <u>Meeting Folder:</u> {meeting_folder_url}<br/> \
            <u>Agenda:</u> {meeting_agenda_url}<br/> \
            <b>REMINDERS:</b> Please mute your phones<br/><br/> \
        Best Regards,<br/> \
        NHTM Education Committee<br/></div>"
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
        mention_id = 0
        for speaker_user in speaker_users:
            speakers_mention += (
                f'<at id="{mention_id}">{speaker_user["displayName"]}</at>, '
            )
            mention_id += 1
        topics_master_mention = f'<at id="{mention_id}">{topics_master_user["displayName"]}</at>'
        attachments = ''#f'<attachment id="{meeting_agenda_item["id"]}">{meeting_agenda_item["name"]}</attachment>'
        self._message = self._message.format(
            meeting_date=meeting_date,
            meeting_day=meeting_day,
            speakers_mention=speakers_mention,
            topics_master_mention=topics_master_mention,
            meeting_folder_url=f'<a href="{meeting_folder_item["webUrl"]}">{meeting_folder_item["name"]}</a>',
            meeting_agenda_url=f'<a href="{meeting_agenda_item["webUrl"]}">{meeting_agenda_item["name"]}</a>',
            attachments=attachments,
        )

    @property
    def subject(self) -> None:
        """get the trimmed subject"""
        return self._subject.strip().strip("\n")

    @property
    def message(self) -> None:
        """get the trimmed message"""
        return self._message.strip().strip("\n")
