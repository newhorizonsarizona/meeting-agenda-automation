import datetime


class DateUtil:
    """This is a utility class for date functions"""

    _today_date: datetime = None

    def __init__(self, today_date: str = None):
        """Initialize the date util"""
        if today_date is None:
            self._today_date = datetime.date.today()
        else:
            self._today_date = datetime.datetime.strptime(today_date, "%m/%d/%Y")

    @property
    def next_tuesday(self):
        """Return the date time for next Tuesday"""
        next_tuesday = self._today_date + datetime.timedelta(
            (1 - self._today_date.weekday()) % 7
        )
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
    def next_tuesday_month(self):
        """Return the month string for next Tuesday"""
        return self.next_tuesday.strftime("%B")
