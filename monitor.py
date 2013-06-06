import os
import sqlite3 as sqlite
from optparse import OptionParser
from sensors.w1 import Wire
from sensors.reading import Reading
from datefuncs.dt import now
from www.appjson import JSONTemps as jsonT

parser = OptionParser()
parser.add_option('-d', '--db', default='templog.db', dest='db',
			help='Database location')
parser.add_option('-i', '--int', default=60, dest='logint', type='int',
			help='Log interval')
parser.add_option('-j', '--json', default='www/static/json/', dest='jsonf',
			help='Location for created JSON files')

def get_temps(wire):
    ''' Retrieve the temperature values from all sensors on the wire'''
    actvals = []
    for dev in wire.devices:
        v = dev.val # retrieving val calls read and updates the sensor
        if dev.isvalid == Reading.VALID:
            actvals.append(v) 
    assert len(actvals) > 0
    return sum(actvals) / len(actvals)

def log_avg(temp, logtime, db):
    ''' log average temperature to the database '''
    with sqlite.connect(db) as con:
        cur = con.cursor()
        cur.execute("INSERT INTO readings VALUES({timestamp}, {temp})".format(
                timestamp = logtime, temp = temp))

def main_func():
    print 'Monitor Running.'
    (options, args) = parser.parse_args()
    log_int = options.logint # Log Interval
    lastlog = 0  # Time we last logged to the db
    wire = Wire()
    temps = [] # current loop temperatures
    jsonf = jsonT(os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                              options.jsonf, 'today.json'))
    while True:
        t = now()
        if t >= lastlog + log_int:
            lastlog = t
            if len(temps) > 0: 
                temp = sum(temps) / len(temps)
                log_avg(temp, t, os.environ['PIMMS_DB'])
                jsonf.add_val(t, temp)
            temps = []
            wire.detect_devices()
        else:
            temps.append(get_temps(wire))

if __name__ == '__main__':
    main_func()
