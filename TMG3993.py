import time
from machine import I2C

class TMG3993:
    
    def __init__(self, i2c):
        self.i2c = I2C(freq=400000)
        REG_RAM = 0x80
        print(REG_RAM)
    def initialie():
        time.sleep(0.06)
        if getDeviceID != 0x2a:
            return False
        return True
    def getDeviceID():
        data = i2c.readfrom(0x92,1)
        return data >> 2
    def enableEngines(enable_bits):
        pben = False
        data = []
        data.append(0x80) #regenable
        if enable_bits & 0x80:
            enable_bits = 0x80
            pben = True
        data.append(0x01 | enable_bits)
        writeto
     
        