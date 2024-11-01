import calendar
import datetime
from datetime import date, timedelta
from loguru import logger


class DateUtil:
    """This is a utility class for date functions"""

    _today_date: date = None

    def __init__(self, today_date: str = None):
        """Initialize the date util"""
        if today_date is None:
            self._today_date = date.today()
        else:
            self._today_date = datetime.datetime.strptime(today_date, "%m/%d/%Y")

    @property
    def next_tuesday(self):
        """Return the date time for next Tuesday"""
        next_tuesday = self._today_date + timedelta((1 - self._today_date.weekday()) % 7)
        return next_tuesday

    def upcoming_tuesdays(self):
        """Return the next four Tuesdays as an array"""
        upcoming_tuesdays = []
        next_date = self.next_tuesday
        i = 1
        while i < 4:
            next_date = next_date + timedelta(1) + timedelta((0 - next_date.weekday()) % 7)
            logger.debug(f"Adding: {next_date}")
            if next_date not in self.get_last_two_tuesdays_of_year():
                upcoming_tuesdays.append(next_date)
            i += 1

        return upcoming_tuesdays

    @property
    def next_tuesday_date(self):
        """Return the date in yyyyMMdd format for next Tuesday"""
        return self.next_tuesday.strftime("%Y%m%d")

    @property
    def next_tuesday_date_us(self):
        """Return the date in MM/dd/yyyy US format for next Tuesday"""
        return self.next_tuesday.strftime("%m/%d/%Y")

    @property
    def next_tuesday_day(self):
        """Return the day for next Tuesday"""
        return self.next_tuesday.strftime("%d")

    @property
    def next_tuesday_month(self):
        """Return the abbreviated month string for next Tuesday"""
        return self.next_tuesday.strftime("%b")

    @property
    def next_tuesday_year(self):
        """Return the year for next Tuesday"""
        return self.next_tuesday.strftime("%Y")

    @property
    def next_month_first_day(self):
        """Return the first date for next month"""
        return (self._today_date.replace(day=1) + timedelta(days=32)).replace(day=1)

    def all_tuesdays(self, for_next_month: bool = False, reverse: bool = True):
        """Returns the list of Tuesdays of the month"""
        first_day_of_month = self._today_date
        if for_next_month:
            first_day_of_month = self.next_month_first_day
        # Calculate the last day of next month
        last_day_of_month = datetime.datetime(
            first_day_of_month.year, first_day_of_month.month, 1
        ) + datetime.timedelta(days=calendar.monthrange(first_day_of_month.year, first_day_of_month.month)[1] - 1)

        # Get all Tuesdays of next month
        tuesdays_of_month = [
            first_day_of_month + timedelta(days=i)
            for i in range((last_day_of_month - first_day_of_month).days + 1)
            if (first_day_of_month + timedelta(days=i)).weekday() == calendar.TUESDAY
        ]
        tuesdays_of_month.sort(reverse=reverse)
        logger.debug(tuesdays_of_month)

        return tuesdays_of_month

    @property
    def last_month_date(self):
        """Return the first date for last month"""
        return (self._today_date.replace(day=28) - datetime.timedelta(days=32)).replace(day=1)

    @property
    def last_month_date_us(self):
        """Return the date in MM/dd/yyyy US format for next Tuesday"""
        return self.last_month_date.strftime("%m/%d/%Y")

    def toastmaster_year(self, meeting_date: date = None):
        """Returns the current toastmaster year"""
        if meeting_date is None:
            meeting_date = self.next_tuesday
        if meeting_date.month > 6 and meeting_date.month <= 12:
            return meeting_date.year + 1
        return meeting_date.year

    def get_last_two_tuesdays_of_year(self):
        """Get the dates for the last two Tuesdays of the current year"""
        # Start with the last day of the given year
        last_day_of_year = datetime.datetime(date.today().year, 12, 31)

        # Find the last Tuesday of the year
        last_tuesday = last_day_of_year - timedelta(days=(last_day_of_year.weekday() - 1) % 7)

        # Find the second last Tuesday by subtracting 7 days from the last Tuesday
        second_last_tuesday = last_tuesday - timedelta(days=7)

        return [second_last_tuesday, last_tuesday]
