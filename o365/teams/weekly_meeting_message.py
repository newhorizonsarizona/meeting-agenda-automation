class WeeklyMeetingMessage:
    """This class is used for storing the weekly meeting message"""

    _subject: str = "{0} - WEEKLY MEETING"
    _message: str = """
                            {0} WEEKLY MEETING @ Cadence Living in Chandler, 100 W Queen Creek Rd., Chandler, AZ 85248\n
                            Dear <at id="0">nhtm_members</at>,\n
                                Please find attached the agenda for the {1} meeting. This is going to be a hybrid meeting. Guests are welcome.\n
                                {2} please place your speech introduction(s) and evaluation forms in the meeting folder. {3} please post the\n
                                meeting theme here.\n
                                <u>Meeting Folder:</u> {4}\n
                                <u>Agenda:</u> {5}\n
                                REMINDERS: Please mute your phones\n
                            Best Regards,\n
                            NHTM Education Committee
                    """

    def __init__(
        self,
        meeting_date,
        meeting_day,
        speakers,
        topics_master,
        meeting_folder,
        meeting_agenda,
    ) -> None:
        """initialize the message assignments"""
        self._subject.format(meeting_date)
        mention_id=1
        speakers_mention=""
        for speaker in speakers:
            speakers_mention += f'<at id="{mention_id}">{speaker}</at>, '
            mention_id += 1
        topics_master_mention = f'<at id="{mention_id}">{topics_master}</at>'
        self._message.format(
            meeting_date,
            meeting_day,
            speakers_mention,
            topics_master_mention,
            meeting_folder,
            meeting_agenda,
        )

    @property
    def subject(self) -> None:
        """get the trimmed subject"""
        return self._subject.strip().strip("\n")

    @property
    def message(self) -> None:
        """get the trimmed message"""
        return self._message.strip().strip("\n")
