import time, datetime
from collections import namedtuple

def now():
    return time.time()

def utc_now():
    return datetime.datetime.utcfromtimestamp(now())

def date_now():
    return datetime.date.fromtimestamp(now())

def utc(t):
    return datetime.datetime.utcfromtimestamp(t)

def valid_year(year): return year > 1900 and year < 2300
def valid_month(month): return month > 0 and month < 13
def valid_day(day): return day > 0 and day < 31
def valid_date(year, month, day):
    if valid_year(year) and valid_month(month) and valid_day(day):
        return True
    return False

def make_day(year, month, day):
    """ Create a namedtuple with 2 datetime objects spaning a day """

    Daytype = namedtuple('DayType', 'start end')
    daystart = datetime.datetime(year, month, day)
    dayend = datetime.datetime(year, month, day, 23, 59, 59)
    return Daytype(daystart, dayend)

def join_date(delim, *args):
    """ Join with delim a list of args into a string """

    return delim.join([str(x) for x in args])

