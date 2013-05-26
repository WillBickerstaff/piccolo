import time, datetime

def now():
    return time.time()

def utc_now():
    return datetime.datetime.utcfromtimestamp(now())

def utc(t):
    return datetime.datetime.utcfromtimestamp(t)
