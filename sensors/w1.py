import os
from sensors.reading import Reading, DecimalReading
from sensors.therm import Thermal
from sensors import W1_LOC

class Wire(object):
    ''' Represent devices on the 1 wire bus

    The wire class when created will read the wire and create each device
    in a set available through wire.devices. Currently supports only thermal
    sensors (see the Thermal class for how to interact with these sensors).
    unknown devices are ignored.

    Calling wire.detect_devices() will repopulate the wire.devices set with
    any new devices. Devices that were already in existince on the wire
    will be retained, any that are no longer there will be removed.
    '''

    #Families supported by the kernel driver
    #THERMAL = {'10': 'DS18S20',
    #           '22': 'DS1822',
    #           '28': 'DS18B20',
    #           '3B': 'DS1825',
    #           '42': 'DS28EA00'}
    #COUNTER = {'1D': 'DS2423'}
    #EEPROM = {'23': 'DS2433',
    #          '2D': 'DS2431',
    #          '1C': 'DS28E04'}
    #BATTERY = {'30': 'DS2760',
    #           '32': 'DS2780',
    #           '3D': 'DS2781'}
    #SWITCH = {'29': 'DS2408',
    #          '3A': 'DS2413'}

    def __init__(self):
        self.devices = set()
        self.devices = self.detect_devices()

    def detect_devices(self, old_dev=set()):
        ''' Return all sensors in /sys/bus/w1/devices

        All sensors are returned as Sensor objects, any  sensor object
        provided in arg old_sensors will be returned if it still exists
        '''

        new_dev = set([x for x in os.listdir(W1_LOC) if 'w1' not in x])
        self.devices = self.__compare_devices(new_dev)
        return self.devices

    def __compare_devices(self, new):
        ''' Return a set of sensor objects that contain only 'live' sensors

        Sensor objects are retained if they are still active, otherwise
        they are removed. any new sensors that are in arg new but not in old 
        will created new sensor objects
        '''

        active = set([s for s in self.devices if s.device in new])
        active_ids = [s.device for s in active]
        new_dev = self.__create_devices([s for s in new if s not in active_ids])
        all_dev = active | new_dev
        assert len(all_dev) == len(new)

        return all_dev

    def __create_devices(self, devices):
        ''' Create the appropriate devices from a list of device ids 

        Arguments:
        devices should be an iterable of strings containing device ids
        '''

        created_devices = []
        for d in devices:
            family = ''
            with open(''.join([W1_LOC,'{dev}/uevent'.format(
                    dev=d)]), 'r') as f:
                lines = [l for l in f]
                family = lines[1].split('=')[1].upper().strip()
            if family in Thermal.FAMILIES:
                created_devices.append(Thermal(d, family))
        return set(created_devices)
