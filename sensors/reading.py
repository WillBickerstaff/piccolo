from datefuncs.dt import now, utc
from collections import namedtuple
class Reading(object):
    ''' Storage for sensor readings with reading status
    
    Reading stores a value provided and maintains a copy of the previous
    reading to use in validation. A status for the current reading is
    maintained to provide a method for determining how trustworthy the 
    reading is. This status should be updated by whatever object is
    implementing the Reading class as validation methods will vary.
    The time of the reading is automatically updated everytime the value
    is changed.

    The class can be initialized with optional keyword arguments:
    val -- the Reading value
    stat -- the reading status using one of the Reading status codes
    
    '''

    # Status codes
    VALID = 0x01
    CRC_ERROR = 0x02
    VARIANCE_ERROR = 0x03
    NO_READING = 0x04
    LOST_SENSOR = 0x5
    UNKNOWN = 0xf6
    last_valid_type = namedtuple('last_valid_type', 'temperature time')

    def __init__(self, **kwargs):
        self.__time = now()
        self.__value  = -999999
        self.__status = Reading.NO_READING
        self.multiplier = 1000
        for k in kwargs:
            if 'val' in k.lower():
                self.__value = kwargs[k]
                self.__time = now()
                next
            if 'stat' in k.lower():
                self.__status = kwargs[k]
                next
            if 'mult' in k.lower():
                self.multiplier = kwargs[k]
                next

        self.__last_valid = Reading.last_valid_type(
            float(self.__value)/self.multiplier, self.time)

    @property
    def float_val(self):
        ''' Returns the reading value / 1000 as a float

        This is useful for sensors that read their values as ints, typically
        these store the number as e.g 23997 representing 23.997 implying the
        decimal point.
        '''
        if self.status == Reading.VALID:
            return float(self.__value)/self.multiplier
        return self.__last_valid.temperature

    @float_val.setter
    def float_val(self, val):
        ''' Set the reading value to the actual decimal reading '''
        self.actval=int(val*self.multiplier)

    @property
    def time(self):
        ''' Retun the time of the reading in the same format as time.time()'''
        return self.__time

    @property
    def utc(self):
        ''' Return the utc of the reading 

        datetime.datetime.utcfromtimestamp(time.time())
        '''
        return utc(self.__time)

    @property
    def status(self):
        ''' Return the Reading status code '''
        return self.__status

    @status.setter
    def status(self, status):
        ''' Set reading status, should be one of the Reading status codes'''
        if status >= Reading.VALID and status <= Reading.LOST_SENSOR:
            self.__status = status
        else:
            self.__status = Reading.UNKNOWN

    @property
    def val(self):
        ''' Return the implied decimal value of the reading.

        Many sensors store there values as integers with an implied decimal
        point so 23.997 would be stored as 23997. val returns the int number
        use float_val to retrieve the value correctly formatted as a float
        '''
        return self.__value

    @val.setter
    def val(self, value):
        ''' Set the implied decimal value of the reading

        You should provide an int representing the value with implied decimal
        point. If you provide a float it will be automatically converted to int
        by multiplying by 1000. e.g if you provide 23.997 the value stored
        will be 23997

        You should follow up by setting the status property as it will
        automatically be set to Reading.UNKNOWN
        '''

        if isinstance(value, float):
            value = int(value * self.multiplier)
        assert isinstance(value, int)
        if self.status == Reading.VALID:
            self.__last_valid = Reading.last_valid_type(self.val,
                                                        self.time)
        self.__value = value
        self.__time = now()
        self.status = Reading.UNKNOWN
