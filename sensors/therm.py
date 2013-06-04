import time
from string import Template
from sensors.base import Sensor, Variance
from sensors.reading import Reading
from sensors import W1_THERM

class Thermal(Sensor):
    ''' Represents a 1 wire digital temperature sensor

    The objected is created with the device id number as the only argument,
    which can be found in /sys/bus/w1/devices, alternatively if you create
    a Wire object from sensors.w1.Wire(), the wire will generate an 
    instance of the correct type of Sensor with id object in its devices
    property. This is the preferred way of creating w1 objects.

    The class provides methods for reading the values and status of the
    sensor data. A Variance object is used with a default value
    of 1 degree variance over 1 second to filter out erroneous readings.
    set this to 0 to disbale it with the variance property
    >>> obj.variance(0,0)

    Thermal sensors create DecimalReading objects for both current and last
    reading properties. The val property of Thermal sensors returns an int
    while the real_val returns the floating point value of the reading as
    does the temperature property.

    TODO Test with DS18S20, DS1822, DS1825, DS28EA00
    '''

    # Families that are valid Thermal Sensors
    FAMILIES = {'10': 'DS18S20', '22': 'DS1822', '28': 'DS18B20',
                '3B': 'DS1825', '42': 'DS28EA00'}
    FACTORS = {'DEFAULT': 1000.0, 'DS18B20': 1000.0}

    def __init__(self, sensor_id, family=None):
        super(Thermal, self).__init__(sensor_id, family)
        self.factor = Thermal.FACTORS[self.family] if self.family in Thermal.FACTORS else Thermal.FACTORS['DEFAULT']
        self._current = Reading()
        self._last = Reading()
        self._variance = Variance(value=1.0, period=1.0)
        self.read()

    def read(self):
        ''' Read the device file from /sys/bus/w1/devices and validate the data

        Read will check the CRC status of the reading and compliance with
        the objects variance property. The current Readind property will
        be updated with the status set to one of the status codes defined
        in the Reading class.

        Does not return any value, use the object properties to access
        the read data.
        '''

        t = time.time()
        try:
            with open(W1_THERM.substitute(dev=self.device),'r') as f:
                self._last = self.current
                lines = [l for l in f]
                reading = self.__check_valid(self.__read_temp(lines[1]),
                                             lines[0])
                if reading.status == Reading.VALID: self._current = reading
        except IOError as e:
            self._current.status = Reading.LOST_SENSOR
            print 'File Error {dev}'.format(dev=self._device)

    def __check_valid(self, check_rdg, crc_line):
        ''' Check for a valid reading and return the reading with status set'''

        if not self.__check_crc(crc_line):
            check_rdg.status = Reading.CRC_ERROR
        elif (self._current.status != Reading.NO_READING and not 
              self._check_variance(check_rdg)):
            check_rdg.status = Sensor.VARIANCE_ERROR
        else:
            check_rdg.status = Reading.VALID
        return check_rdg

    def __check_crc(self, line):
        ''' Check the CRC status provided by the sensor '''

        return True if line[-4:-1] == 'YES' else False

    def __read_temp(self, line):
        ''' Get the temperature reading from the sensor and return as int'''

        return Reading(val = int(line.split(" ")[9][2:]),
                       factor = self.factor)


    @property
    def temperature(self):
        ''' Returns the current temperature as a float'''

        self.read()
        return self.current.real_val

    @property
    def family(self):
        ''' Get the Sensor type - DS18B20, DS18S20 etc '''

        if self._family is None:
            self._detect_family
        return Thermal.FAMILIES[self._family]

    @family.setter
    def family(self, family):
        ''' Set the sensor family, must be one of keys in Thermal.FAMILIES'''

        family = str(family)
        if family in  Thermal.FAMILIES:
            self._family = family
            return True
        return False
