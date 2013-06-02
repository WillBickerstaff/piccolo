import os
import sqlite3 as sqlite
from sensors.ds18b20 import Thermal as DS18B20
from sensors.reading import Reading
from datefuncs.dt import now

def get_sensors(old_sensors=set()):
    ''' Return all sensors in /sys/bus/w1/devices
    
    All sensors are returned as ds18b20.Sensor objects, any  sensor object
    provided in arg old_sensors will be returned if it still exists
    '''

    new_sensors = [x for x in os.listdir("/sys/bus/w1/devices") if 'w1' not in x]
    return compare_sensors(set(new_sensors), old_sensors)

def compare_sensors(new, old):
    ''' Return a set of sensor objects that contain only 'live' sensors

    Sensor objects are retained from arg old if the are still active, otherwise
    they are removed. any new sensors that are in arg new but not in old create
    new sensor objects
    '''

    active = set([s for s in old if s.device in new])
    active_ids = [s.device for s in active]
    new_sen = set([DS18B20(s) for s in new if s not in active_ids])
    all_sen = active | new_sen
    assert len(all_sen) == len(new)
    
    return all_sen

def get_temps(sensors):
    ''' Retrieve the temperature values from all sensors '''
    actvals = []
    for s in sensors:
        v = s.val # retrieving val calls read and updates the sensor
        if s.isvalid == Reading.VALID:
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
    sensors = []
    temps = [] # current loop temperatures
    while True:
        t = now()
        if t >= lastlog + log_int:
            sensors = get_sensors(sensors)
            lastlog = t
            if len(temps) > 0: log_avg(temps, t, os.environ['PIMMS_DB'])
            temps = []
            sensors = get_sensors(sensors)
        else:
            temps.append(get_temps(sensors))

if __name__ == '__main__':
    main_func()
