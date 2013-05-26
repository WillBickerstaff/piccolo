from sensors.reading import Reading
from datefuncs.dt import now

class Variance(object):

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
        diff = val1 - val2 if val1 > val2 else val2 - val1
        assert diff >= 0
        return diff <= (self.value * self.period) * timediff

class Sensor(object):
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
        if not self.__check_crc(crc_line):
            check_rdg.status = Reading.CRC_ERROR
        elif not (self.__check_variance(check_rdg)):
            check_rdg.status = Sensor.VARIANCE_ERROR
        else:
            check_rdg.status = Reading.VALID
        return check_rdg

    def __check_variance(self, reading):
        if self.last.status == Reading.VALID:
            return self.__variance.check_vals(self.last.temperature,
                                            self.current.temperature,
                                            self.current.time - self.last.time)
        return True


    def __check_crc(self, line):
        return True if line[-4:-1] == 'YES' else False

    def __read_temp(self, line):
        return Reading(val = int(line.split(" ")[9][2:]))

    @property
    def device(self):
        return self.__device

    @property
    def current(self):
        return self.__current

    @property
    def last(self):
        return self.__last

    @property
    def isvalid(self):
        return self.current.status

    @property
    def temperature(self):
        return self.current.temperature

    @property
    def val(self):
        return self.current.val
