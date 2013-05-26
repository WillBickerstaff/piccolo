from datefuncs.dt import now, utc
from collections import namedtuple
class Reading(object):
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
        for k in kwargs:
            if 'val' in k.lower():
                self.__value = kwargs[k]
                self.__time = now()
                next
            if 'stat' in k.lower():
                self.__status = kwargs[k]
                next
        self.__last_valid = Reading.last_valid_type(float(self.__value)/1000,
                                                    self.time)

    @property
    def temperature(self):
        if self.status == Reading.VALID:
            return float(self.__value)/1000
        return self.__last_valid.temperature
    @temperature.setter
    def temperature(self, value, status):
        if isinstance(value, float):
            value = int(value * 1000)
        assert isinstance(value, int)
        self.__value = value
        self.__time = now()
        self.status = status
        if self.status == Reading.VALID:
            self.__last_valid = Reading.last_valid_type(self.temperature,
                                                        self.time)

    @property
    def time(self):
        return self.__time
    @property
    def utc(self):
        return utc(self.__time)

    @property
    def status(self):
        return self.__status

    @status.setter
    def status(self, status):
        if status >= Reading.VALID and status <= Reading.LOST_SENSOR:
            self.__status = status
        else:
            self.__status = Reading.UNKNOWN

    @property
    def val(self):
        return self.__value
