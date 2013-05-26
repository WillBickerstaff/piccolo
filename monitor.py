import os, json
import sqlite3 as sqlite
from sensors.ds18b20 import Sensor as DS18B20
from sensors.reading import Reading
from datefuncs.dt import now


def get_sensors(old_sensors=set()):
    new_sensors = [x for x in os.listdir("/sys/bus/w1/devices") if 'w1' not in x]
    new_sensors.sort(key = lambda x: x)
    return compare_sensors(set(new_sensors), old_sensors)

def compare_sensors(new, old):
    active = set(s for s in old if s.device in new)
    active_ids = [s.device for s in active]
    new_sen = set(DS18B20(s) for s in new if s not in active)
    all_sen = active | new_sen
    
    return all_sen

def get_temps(sensors):
    actvals = []
    for s in sensors:
        s.read()

        if s.isvalid == Reading.VALID:
            actvals.append(s.val)
    assert len(actvals) > 0
    return sum(actvals) / len(actvals)


def log_avg(temps, logtime, db):
    avgtemp = sum(temps) / len(temps)
    with sqlite.connect(db) as con:
        cur = con.cursor()
        cur.execute("INSERT INTO readings VALUES({timestamp}, {temp})".format(
                timestamp = logtime, temp = avgtemp))

def sensor_wait(sensors):
    return sum(s.update_interval for s in sensors)

if __name__ == '__main__':
    print 'Monitor Running.'
    log_int = 60
    lastlog = 0
    sensors = get_sensors()
    temps = []
    while True:
        sensors = get_sensors(sensors)
        if len(sensors) > 0:
            temps.append(get_temps(sensors))
            t = now()
            if t >= (lastlog + log_int) - (sensor_wait(sensors)):
                lastlog = t
                log_avg(temps, t, os.environ['PIMMS_DB'])
                temps = []
