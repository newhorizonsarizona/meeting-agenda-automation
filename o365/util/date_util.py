import calendar
import datetime
from loguru import logger
from datetime import date, timedelta
from time import strptime


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
