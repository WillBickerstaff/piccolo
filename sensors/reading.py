import time
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
    last_valid_type = namedtuple('last_valid_type', 'val time')

    def __init__(self, **kwargs):
        self._time = time.time()
        self._val  = -999999
        self._status = Reading.NO_READING
        if 'val' in kwargs:
            if isinstance(kwargs['val'], int):
                self.val = kwargs['val']
                self._time = time.time()
                for k in kwargs:
                    if 'stat' in k:
                        self._status = kwargs[k]
                        break

        self._last_valid = Reading.last_valid_type(self.val, self.time)

    @property
    def time(self):
        ''' Retun the time of the reading in the same format as time.time()'''
        return self._time

    @property
    def utc(self):
        ''' Return the utc of the reading 

        datetime.datetime.utcfromtimestamp(time.time())
        '''
        return datetime.datetime.utcfromtimestamp(self._time)

    @property
    def status(self):
        ''' Return the Reading status code '''
        return self._status

    @status.setter
    def status(self, status):
        ''' Set reading status, should be one of the Reading status codes'''
        if status >= Reading.VALID and status <= Reading.LOST_SENSOR:
            self._status = status
        else:
            self._status = Reading.UNKNOWN

    @property
    def val(self):
        ''' Return the implied decimal value of the reading.

        Many sensors store there values as integers with an implied decimal
        point so 23.997 would be stored as 23997. val returns the int number
        use real_val to retrieve the value correctly formatted as a float
        '''
        return self._val


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
        assert isinstance(value, int)
        if self.status == Reading.VALID:
            self._last_valid = Reading.last_valid_type(self.val, self.time)
        self._val = value
        self._time = time.time()
        self.status = Reading.UNKNOWN

    @property
    def last_valid(self):
        return self._last_valid

class DecimalReading(Reading):

    def __init__ (self, **kwargs): 
        self._factor = 1000.0
        super(DecimalReading, self).__init__()
        for k in kwargs:
            if k == 'val':
                self.val = kwargs[k]
                next
            if k == 'real_val':
                self.real_val = kwargs[k]
                next
            if 'stat' in k:
                self.status = kwargs[k]
                next
            if 'mult' in k or 'fact' in k:
                self.fact = kwargs[k]
                next



    @property
    def real_val(self):
        return self.val / self.factor

    @real_val.setter
    def real_val(self, val):
        self.val = int(val * self.factor)

    @property
    def factor(self):
        return self._factor

    @factor.setter
    def factor(self, val):
        self._factor = float(val)

    @property
    def last_valid(self):
        return Reading.last_valid_type(super.last_valid.val / self.factor,
                                       super.last_valid.time)
