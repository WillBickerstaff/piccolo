from string import Template
from sensors.reading import Reading
from sensors import W1_LOC

class Sensor(object):
    # Location of the file where sensor data is
    DEVICE_FILE = Template(''.join([W1_LOC, '$dev/w1_slave']))
    # Location of the file that contains sensor type
    UEVENT_FILE = Template(''.join([W1_LOC, '$dev/uevent']))


    def __init__(self, sensor_id, family=None):
        self._device = sensor_id
        self._family = family
        self._current = Reading()
        self._last = Reading()
        self._variance = Variance()
        self.adj = 0

    def _check_variance(self, reading):
        ''' Check variance is permitted between this reading and the last.'''

        if self.last.status == Reading.VALID:
            return self._variance.check_vals(self.last.real_val,
                                            self.current.real_val,
                                            self.current.time - self.last.time)
        return True
    @property
    def device(self):
        '''Returns the device id a s a string.'''

        return self._device

    @property
    def isvalid(self):
        '''Return the status code of the current reading

        Status codes are defined in the Reading object
        '''
        return self.current.status

    @property
    def current(self):
        '''Returns the current reading as a Reading object.'''

        return self._current

    @property
    def last(self):
        '''Returns the last reading as a a Reading object.'''
        return self._last

    @property
    def val(self):
        ''' Return the sensor current value this as int. '''

        self.read()
        return self.current.val

    @property
    def current(self):
        '''Returns the current sensor Reading object '''

        return self._current

    @property
    def last(self):
        '''Return the previous reading as a Reading object'''

        return self._last

    def variance(self, value, period):
        ''' Set the permitted variance parameters for this sensor.

        >>> s = Sensor('somesensorid')
        >>> s.variance(0.5, 1)
        will produce a Variance that allows a 0.5C difference of a 1 second
        period,a 1C difference over 2 second and 1.5C  difference over 3
        seconds... etc.

        Same functionallity as:
        obj.variance.value = 1
        obj.variance.period = 1
        '''

        self._variance.value = value
        self._variance.period = period

    @property
    def variance(self):
        ''' Return the Variance object for this sensor.'''

        return self._variance


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
        self.period = 0
        self.value = 0
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
        if self.period == 0 and self.value == 0: return True
        diff = val1 - val2 if val1 > val2 else val2 - val1
        assert diff >= 0
        return diff <= (self.value * self.period) * timediff
