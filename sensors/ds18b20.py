from sensors.reading import Reading
from datefuncs.dt import now

class Variance(object):
    ''' Define an allowable variance between to values over a period

    Arguments:
    val -- the allowed variance as a numeric type
    period -- The period over which that variance applies as a numeric type

    example:
    >>> v = Variance(val = 1, period = 1)
    will produce a Variance object that allows a value 1 difference of a
    1 second period,a 2 value difference over 2 second and 3 value difference
    over 3 seconds... etc.
    '''

    def __init__(self, **kwargs):
        self.period = 1.0
        self.value = 1.0
        for k in kwargs:
            if 'val' in k.lower():
                self.value = kwargs[k]
                next
            if 'per' in k.lower():
                self.period = kwargs[k]
                next

    def check_vals(self, val1, val2, timediff):
        ''' Check the variance between 2 readings in a period meet the
        variance requirements

        Returns True if the variance meets the requirements of the object
        otherwise False.

        Example:
        >>> v = Variance(val = 1, period = 1)
        >>> valid = v.check_vals(1, 1.5, 1)
        >>> # valid == True
        >>>
        >>> v = Variance(val = 1, period = 1)
        >>> valid = v.check_vals(1, 3, 1)
        >>> # valid == False
        >>>
        >>> v = Variance(val = 1, period = 1)
        >>> valid = v.check_vals(1, 2, 3)
        >>> # valid == True
        '''
        diff = val1 - val2 if val1 > val2 else val2 - val1
        assert diff >= 0
        return diff <= (self.value * self.period) * timediff

class Sensor(object):
    ''' Represents a DS18B20 1 wire digital temperature sensor

    The objected is created with the device id number as the only argument,
    which can be found in /sys/bus/w1/devices

    The class provides methods for reading the values and status of the
    sensor data. A Variance object is used with a default value
    of 1 degree variance over 1 second to filter out erroneous readings.
    set this to something high to disbale it with the variance property
    >>> obj.variance(1000,1)
    which will allow a variance of 1000 degrees every second.

    Should also work with DS18S20, though not tested.
    '''


    UPDATE_INTERVAL = .75

    def __init__(self, sensor_id):
        self.__device = sensor_id
        self.adj = 0
        self.__current = Reading()
        self.__last = Reading()
        self.__variance = Variance()
        self.read(True)
        self.update_interval = Sensor.UPDATE_INTERVAL

    def read(self, force=False):
        ''' Read the device file from /sys/bus/w1/devices and validate the data

        Will only re-read a device if the last read is greater than 
        update_interval. A read can be forced by calling read(True)

        Does not return any value, use the object properties to access
        the read data.
        '''

        # Only read if outside update_interval and not forced
        if (not force and self.current.status != Reading.NO_READING and
            self.last.time > now() - Sensor.UPDATE_INTERVAL):
            return
        try:
            with open('/sys/bus/w1/devices/{sensor}/w1_slave'.format(
                    sensor=self.device)) as device_file:
                self.__last = self.current
                lines = [l for l in device_file]
                reading = self.__check_valid(self.__read_temp(lines[1]),
                                             lines[0])
                if reading.status == Reading.VALID: self.__current = reading
        except IOError as e:
            self.__current.status = Reading.LOST_SENSOR

    def __check_valid(self, check_rdg, crc_line):
        ''' Check for a valid reading and return the reading with status set'''

        if not self.__check_crc(crc_line):
            check_rdg.status = Reading.CRC_ERROR
        elif not (self.__check_variance(check_rdg)):
            check_rdg.status = Sensor.VARIANCE_ERROR
        else:
            check_rdg.status = Reading.VALID
        return check_rdg

    def __check_variance(self, reading):
        ''' Check variance is permitted between this reading and the last.'''

        if self.last.status == Reading.VALID:
            return self.__variance.check_vals(self.last.float_val,
                                            self.current.float_val,
                                            self.current.time - self.last.time)
        return True


    def __check_crc(self, line):
        ''' Check the CRC status provided by the sensor '''

        return True if line[-4:-1] == 'YES' else False

    def __read_temp(self, line):
        ''' Get the temperature reading from the sensor and return as int'''

        return Reading(val = int(line.split(" ")[9][2:]))

    @property
    def device(self):
        '''Returns the device id a s a string.'''
        return self.__device

    @property
    def current(self):
        '''Returns the current reading as a Reading object.'''
        return self.__current

    @property
    def last(self):
        '''Returns the last reading as a a Reading object.'''
        return self.__last

    @property
    def isvalid(self):
        '''Return the status code of the current reading

        Status codes are defined in the Reading object
        '''
        return self.current.status

    @property
    def temperature(self):
        ''' Returns the current temperature as a float'''
        return self.current.float_val

    @property
    def val(self):
        ''' Return the sensor current value this is an int with implied
        decimal point. '''

        return self.current.val

    @property
    def variance(self):
        ''' Return the Variance object for this sensor.'''
        return self.__variance

    def variance(self, value, period):
        ''' Set the permitted variance parameters for this sensor.

        >>> s = Sensor('somesensorid')
        >>> s.variance(0.5, 1)
        will produce a Variance that allows a 0.5C difference of a 1 second
        period,a 1C difference over 2 second and 1.5C  difference over 3
        seconds... etc.
        '''

        self.__variance.value = value
        self.__variance.period = period
