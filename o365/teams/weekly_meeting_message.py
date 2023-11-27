class WeeklyMeetingMessage:
    """This class is used for storing the weekly meeting message"""

    _subject: str = "{0} - WEEKLY MEETING"
    _message: str = """
                            {0} WEEKLY MEETING @ Cadence Living in Chandler, 100 W Queen Creek Rd., Chandler, AZ 85248
                            Dear New Horizons Toastmasters Club members,
                                Please find attached the agenda for the {1} meeting. This is going to be a hybrid meeting. Guests are welcome.
                                {2} please place your speech introduction(s) and evaluation forms in the meeting folder. {3} please post the
                                meeting theme here.
                                Meeting Folder: {4}
                                Agenda: {5}
                                REMINDERS: Please mute your phones
                            Best Regards,
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
        self._message.format(
            meeting_date,
            meeting_day,
            speakers,
            topics_master,
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
