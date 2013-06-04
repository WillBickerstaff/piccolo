import os
from string import Template

W1_LOC = '/sys/bus/w1/devices/'
W1_THERM = Template(''.join([W1_LOC, '$dev/w1_slave']))
W1_UEVENT = Template(''.join([W1_LOC, '$dev/uevent']))
