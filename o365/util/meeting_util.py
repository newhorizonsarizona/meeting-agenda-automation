import datetime
import os

from o365.util.date_util import DateUtil


class MeetingUtil:
    """This class contains some meeting utilities"""

    _next_tuesday: datetime

    def __init__(self, next_tuesday = None):
        """Initialize the meeting utils class"""
        self._next_tuesday = next_tuesday  if next_tuesday is not None else DateUtil().next_tuesday

    @property
    def next_tuesday_meeting_docs(self):
        """Return the meeting docs folder name for next Tuesday"""
        return self._next_tuesday.strftime("%Y-%m-%d Meeting Docs")

    @property
    def next_tuesday_meeting_agenda_excel(self):
        """Return the meeting agenda excel file name for next Tuesday"""
        return self._next_tuesday.strftime("NHTM Online Agenda %m-%d-%Y.xlsx")

    @property
    def agenda_template_excel(self):
        """Return the name of the meeting agenda template excel file name"""
        agenda_template_file_name: str = self._next_tuesday.strftime(
            "NHTM Online Agenda Template %Y.xlsx"
        )
        if self.is_next_meeting_reverse:
            agenda_template_file_name = self._next_tuesday.strftime(
                "NHTM Online Agenda Reverse Template %Y.xlsx"
            )
        return agenda_template_file_name

    @property
    def is_next_meeting_reverse(self):
        """Return if the next meeting is a reverse meeting"""
        if os.environ.get("REVERSE_MEETING") is not None:
            return True
        return False
