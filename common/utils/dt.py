# Utilities for date time
from datetime import datetime

import pytz


class DT:
    DATE_FORMAT = "%Y-%m-%d"
    DT_FORMAT = "%Y-%m-%dT%H:%M:%S"
    DT_TZ_FORMAT = "%Y-%m-%dT%H:%M:%S%z"
    DT_SPACE_FORMAT = "%Y-%m-%d %H:%M:%S"

    @staticmethod
    def x_years_ago(date, x):
        return DT.x_years_later(date, -x)

    @staticmethod
    def x_years_later(date, x):
        try:
            return date.replace(year=date.year + x)
        except ValueError:
            # This block is executed if replacing the year creates an invalid date (e.g., Feb 29 to a non-leap year)
            if date.month == 2 and date.day == 29:
                # Move the date to February 28 of the target year
                return date.replace(year=date.year + x, day=28)
            else:
                raise

    @staticmethod
    def to_date_str(dt):
        return dt.strftime(DT.DATE_FORMAT)

    @staticmethod
    def to_dt_str(dt):
        return dt.strftime(DT.DT_FORMAT)

    @staticmethod
    def to_dt_tz_str(dt):
        dt_with_tz = DT.add_tz(dt)
        dtstr = dt_with_tz.strftime(DT.DT_TZ_FORMAT)
        return dtstr[:-2] + ":" + dtstr[-2:]

    @staticmethod
    def from_date_str(date_str):
        return datetime.strptime(date_str, DT.DATE_FORMAT)

    @staticmethod
    def from_dt_str(date_str):
        return datetime.strptime(date_str, DT.DT_FORMAT)

    @staticmethod
    def from_dt_tz_str(date_str):
        dt_with_tz = datetime.strptime(date_str, DT.DT_TZ_FORMAT)
        return DT.add_tz(dt_with_tz)

    @staticmethod
    def from_dt_space_str(date_str):
        dt = datetime.strptime(date_str, DT.DT_SPACE_FORMAT)
        return DT.add_tz(dt)

    @staticmethod
    def add_tz(dt: datetime, tz="utc") -> datetime:
        if dt.tzinfo is None:
            return pytz.timezone(tz).localize(dt)
        else:
            return dt.astimezone(pytz.timezone(tz))

    @staticmethod
    def now() -> datetime:
        return datetime.now()
