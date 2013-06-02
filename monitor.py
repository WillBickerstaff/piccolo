import os
import sqlite3 as sqlite

from sensors.w1 import Wire
from sensors.reading import Reading
from datefuncs.dt import now


def get_temps(wire):
    ''' Retrieve the temperature values from all sensors on the wire'''
    actvals = []
    for dev in wire.devices:
        v = dev.val # retrieving val calls read and updates the sensor
        if dev.isvalid == Reading.VALID:
            actvals.append(v) 
    assert len(actvals) > 0
    return sum(actvals) / len(actvals)

def log_avg(temps, logtime, db):
    ''' log average temperature to the database '''
    avgtemp = sum(temps) / len(temps)
    with sqlite.connect(db) as con:
        cur = con.cursor()
        cur.execute("INSERT INTO readings VALUES({timestamp}, {temp})".format(
                timestamp = logtime, temp = avgtemp))

def main_func():
    print 'Monitor Running.'
    log_int = 60 # Log Interval
    lastlog = 0  # Time we last logged to the db
    wire = Wire()
    temps = [] # current loop temperatures
    while True:
        t = now()
        if t >= lastlog + log_int:
            lastlog = t
            if len(temps) > 0: log_avg(temps, t, os.environ['PIMMS_DB'])
            temps = []
            wire.detect_devices()
        else:
            temps.append(get_temps(wire))

if __name__ == '__main__':
    main_func()
