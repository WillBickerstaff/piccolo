import time, datetime
from collections import namedtuple

Daytype = namedtuple('DayType', 'start end')
DATEFORMAT = '%Y-%m-%d %H:%M:%S'

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

def make_day(day):
    """ Create a namedtuple with 2 datetime objects spaning a day """

    daystart = datetime.datetime(day.year, day.month, day.day)
    dayend = datetime.datetime(day.year, day.month, day.day, 23, 59, 59)
    return Daytype(daystart, dayend)

def timestamp_day(timestamp):
    d = utc(timestamp)
    day = makeday(d)
    return DayType(mktime(day.start), mktime(day.end))

def join_date(delim, *args):
    """ Join with delim a list of args into a string """

    return delim.join([str(x) for x in args])

def webformat(d):
    return d.strftime(DATEFORMAT)

def web2time(timestring):
    return time.mktime(time.strptime(timestring, DATEFORMAT))

def time2web(timestamp):
    return webformat(datetime.datetime.utcfromtimestamp(timestamp))

def is_today(timestamp):
    today = timestamp_day(now())
    return today.start < timestamp < today.end
