import os, json, time
import sqlite3 as sqlite
from sensors.ds18b20 import Sensor as DS18B20
from sensors.reading import Reading
from datefuncs.dt import now

def get_sensors(old_sensors=set()):
    ''' Return all sensors in /sys/bus/w1/devices
    
    All sensors are returned as ds18b20.Sensor objects, any  sensor object
    provided in arg old_sensors will be returned if it still exists
    '''

    new_sensors = [x for x in os.listdir("/sys/bus/w1/devices") if 'w1' not in x]
    new_sensors.sort(key = lambda x: x)
    return compare_sensors(set(new_sensors), old_sensors)

def compare_sensors(new, old):
    ''' Return a set of sensor objects that contain only 'live' sensors

    Sensor objects are retained from arg old if the are still active, otherwise
    they are removed. any new sensors that are in arg new but not in old create
    new sensor objects
    '''

    active = set(s for s in old if s.device in new)
    active_ids = [s.device for s in active]
    new_sen = set(DS18B20(s) for s in new if s not in active)
    all_sen = active | new_sen
    
    return all_sen

def get_temps(sensors):
    ''' Retrieve the temperature values from all sensors '''
    actvals = []
    for s in sensors:
        s.read()

        if s.isvalid == Reading.VALID:
            # retrieve val, not temperature as we want to store it in the db as
            # an int
            actvals.append(s.val) 
    assert len(actvals) > 0
    return sum(actvals) / len(actvals)


def log_avg(temps, logtime, db):
    ''' log average temperature to the database '''
    avgtemp = sum(temps) / len(temps)
    with sqlite.connect(db) as con:
        cur = con.cursor()
        cur.execute("INSERT INTO readings VALUES({timestamp}, {temp})".format(
                timestamp = logtime, temp = avgtemp))

if __name__ == '__main__':
    print 'Monitor Running.'
    log_int = 60 # Log Interval
    lastlog = 0  # Time we last logged to the db
    sensors = get_sensors() # set of available sensors
    temps = [] # current loop temperatures
    
    while True:
        if len(sensors) > 0:
            t = now()
            temps.append(get_temps(sensors))
            if t >= lastlog + float(log_int):
                sensors = get_sensors(sensors) # Look for new / missing sensors
                lastlog = now()
                log_avg(temps, t, os.environ['PIMMS_DB'])
                temps = []
            time.sleep(0.1)
