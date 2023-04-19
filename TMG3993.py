import time

class TMG3993:
    
    def __init__(self, i2c):
        self.i2c = i2c
        


    '''
    bool TMG3993::initialize(void) {
        //wait 5.7ms
        delay(6);
        //check chip id
        if (getDeviceID() != 0x2a) {
            return false;
        }
        return true;
    }
    '''
    def initialise(self):
        time.sleep(0.06)
        if self.getDeviceID() != 0x2a:
            return False
        return True

    '''
    uint8_t TMG3993::getDeviceID(void) {
    uint8_t data;
    readRegs(REG_ID, &data, 1);
    return (data >> 2);
    }
    '''
    def convert(data):
        int_val = int.from_bytes(data,"big")
        return int_val
    
    def getDeviceID(self):
        data = self.i2c.readfrom_mem(0x39,0x92,1) #REG_ID, &data 1
        int_val = int.from_bytes(data,"big")
        return int_val >> 2

    def enableEngines(self, enable_bits):
        pben = False
        data = []
        data.append(0x80) #regenable
        if enable_bits & 0x80:
            enable_bits = 0x80
            pben = True
        data.append(0x01 | enable_bits)
        print(data)
        self.i2c.writeto_mem(0x39, 0x80,  data[1].to_bytes(1,"little"))

        if not pben:
            time.sleep(0.07)
     
    def setADCIntegrationTime(self, atime):
        data = [0x81,atime]   #REG_ATIME
        self.i2c.writeto(data, 2)
    def setWaitTime(self,wtime):
        data = [0x83,wtime]  #REG_WTIME
        self.i2c.writeto(data, 2)
    def enableWaitTime12xFactor(self, enable):
        data = [0x83]   #REG_WTIME
        if enable:
            data.append(0x62)
        else:
            data.append(0x60)
        self.i2c.writeto(data, 2)
    def getInterruptPersistenceReg(self):
        data = self.i2c.readfrom(0x8C, 1)
        return data
    def setInterruptPersistenceReg(self,pers):
        data = [0x8C, pers]
        self.i2c.writeto(data, 2)
    def getControlReg(self):
        data = self.i2c.readfrom_mem(0x39,0x8F, 1)
        valu =int.from_bytes(data,"big")
        return valu
    def setControlReg(self,control):
        data = [0x8F, control]
        self.i2c.writeto_mem(data, 2)

    def getCONFIG2(self):
        data = self.i2c.readfrom(0x90, 1)
        return data

    def setCONFIG2(self,config):
        data = [0x90, config]
        self.i2c.writeto(data, 2)

    def getCONFIG3(self):
        data = self.i2c.readfrom(0x9F, 1)
        return data
    def setCONFIG3(self,config):
        data = [0x9F, config]
        self.i2c.writeto(data, 2)
    def getSTATUS(self):
        data = self.i2c.readfrom(0x93, 1)
        return data
    def clearPatternBurstInterrupts(self):
        data = self.i2c.readfrom(0xE3, 1)
    def forceAssertINTPin(self):
        data = self.i2c.readfrom(0xE4, 1)
    def clearProximityInterrupts(self):
        data = self.i2c.readfrom(0xE5, 1)
    def clearALSInterrupts(self):
        data = self.i2c.readfrom(0xE6, 1)
    def clearAllInterrupts(self):
        data = self.i2c.readfrom(0xE7, 1)

    def setupRecommendedConfigForProximity(self):
        # self.setProximityInterruptThreshold()
        self.setProximityPulseCntLen(63,1)
        config2 = self.getCONFIG2()
        # config2 &= (3 << 4)
        config2 |= (3 << 4)
        self.setCONFIG2(config2)
        # this will change the response speed of the detection
        # smaller value will response quickly, but may raise error detection rate
        # bigger value will repsonse slowly, but will ensure the detection is real.
        self.setInterruptPersistenceReg(0xa << 4)
    def setProximityInterruptThreshold(self,low,high):
        data = [0x89,low]
        self.i2c.writeto(data, 2)

        data = [0x8B,high]
        self.i2c.writeto(data, 2)
    def setProximityPulseCntLen(self,cnt,length):
        data = [0x8E]
        if cnt > 63:
            cnt = 63
        if length > 3:
            length = 3
        data.append((cnt & 0x3f) | (length & 0xb0))
        self.i2c.writeto(data, 2)
    def getProximityRaw(self):
        data = self.i2c.readfrom(0x9C, 1)
        return data
    def setALSInterruptThreshold(self,low,high):
        data = [0x84, low & 0xff, low >> 8, high & 0xff, high >> 8]
        self.i2c.writeto(data, 2)
    def getRGBCRaw(self):
        data = self.i2c.readfrom_mem(0x39,0x94, 8)
        '''
        print(data[0],data[1],data[2],data[3],data[4])
        int_val = int.from_bytes(data[0],"big")
        int_val2 = int.from_bytes(data[2],"big")
        int_val4 = int.from_bytes(data[4],"big")
        int_val6 = int.from_bytes(data[6],"big")
        print(int_val,int_val2,int_val4,int_val6)
        C = self.convert(data[1])# << 8# | self.convert(data[0])
        R = self.convert(data[3]) << 8 | self.convert(data[2])
        G = self.convert(data[5]) << 8 | self.convert(data[4])
        B = self.convert(data[7]) << 8 | self.convert(data[6])
        '''
        C = (data[1] << 8) | data[0]
        R = (data[3] << 8) | data[2]
        G = (data[5] << 8) | data[4]
        B = (data[7] << 8) | data[6]
        return R, G, B, C
    def getLux1(self,R,G,B,C):
        data = self.i2c.readfrom_mem(0x39,0x81, 1)
        ms = (256 - int.from_bytes(data,"big")) * float(2.78)
        data = self.getControlReg()
        gain = 0
        if data & 0x3 == 0x0:
            gain = 1
        elif data & 0x3 == 0x1:
            gain = 4
        elif data & 0x3 == 0x2:
            gain = 16
        elif data & 0x3 == 0x3:
            gain = 64
        else:
            gain = 1
        IR = int()
        CPL = float()
        Y = float()
        L = float()

        IR = R + G +B
        IR = (IR-C)/2
        if IR < 0:
            IR = 0
        Y = 0.362 * (R-IR) + 1*(G-IR) + 0.136 * (B-IR)
        CPL = ms * gain/412
        L = Y / CPL
        return int(L)
    def getLux(self):
        R, G, B, C = self.getRGBCRaw()
        return self.getLux1(R, G, B, C)
    def getCCT(self, R, G, B, C):
        IR = R + G + B
        IR =  (IR - C)/2
        if IR < 0:
            IR = 0

        lR = R
        lG = G
        lB = B
        minV = min(lR,lB)
        if IR < minV:
            IR = minV - 0.1
        rate = float(lB - IR) / float(lR - IR)
        return 2745 * int(rate)+ 2242
    def getCCT(self):
        R, G, B, C = self.getRGBCRaw()
        return self.getCCT(R,G,B,C)