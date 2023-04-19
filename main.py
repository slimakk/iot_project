from machine import Pin, I2C
from TMG3993 import *
import time
i2c = I2C(0, scl=Pin(5), sda=Pin(4), freq=400000)

print(i2c.scan())

sensor = TMG3993(i2c)

print(sensor.getDeviceID())

sensor.enableEngines(0x01 | 0x02 | 0x10)

    
print(sensor.getRGBCRaw())
while 1:
    time.sleep(1)
    print(sensor.getLux())