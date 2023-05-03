from machine import Pin, I2C
from TMG3993 import *
from my9221 import MY9221
import time
import network
import ujson
import microcoapy
import coap_macros
import sdcard
import uos

#CoAP server key information
_SERVER_IP ='86.49.182.194'
_SERVER_PORT = 36105  #5683 36105 default CoAP port
_COAP_POST_URL = 'api/v1/IoT_04/telemetry' # fill your Device name, select based on your workstation
_COAP_GET_REQ_URL = 'api/v1/IoT_04/attributes' # fill your Device name, select based on your workstation
_COAP_AUT_PASS = 'authorization=IoT_04' # fill your Device name, select based on your workstation

# SD card
cs = machine.Pin(15, machine.Pin.OUT) 
spi = machine.SPI(1,
                  baudrate=1000000,
                  polarity=0,
                  phase=0,
                  bits=8,
                  firstbit=machine.SPI.MSB,
                  sck=machine.Pin(10),
                  mosi=machine.Pin(11),
                  miso=machine.Pin(12))

sd = sdcard.SDCard(spi, cs)
vfs = uos.VfsFat(sd)
uos.mount(vfs, "/sd")

# create file with light intensity
with open("/sd/lux.txt", "w") as file:
        file.write(f"Light_intensity:\r\n")


# button for upload
BUTTON1 = Pin(20, Pin.IN)

# Sensor
i2c = I2C(0, scl=Pin(5), sda=Pin(4), freq=400000)
print(i2c.scan())

sensor = TMG3993(i2c)
sensor.enableEngines(0x01 | 0x02 | 0x10)

# Ledbar
ledbar = MY9221(di=Pin(3), dcki=Pin(2))


# Button callback
def pinPressedCallback(pin):
    lux = sensor.getLux()
    with open("/sd/lux.txt", "a") as file:
        file.write(f"Lux:{lux}\r\n")
    
    json = createJSON()
    sendPostRequest(client, json)
    client.poll(1000, pollPeriodMs=1)
    

#Coap POST Message function.
def sendPostRequest(client, json):
    messageId = client.post(_SERVER_IP, _SERVER_PORT, _COAP_POST_URL, json,
                                   None, coap_macros.COAP_CONTENT_FORMAT.COAP_APPLICATION_JSON)
    print("[POST] Message Id: ", messageId)


#Coap PUT Message function.
def sendPutRequest(client):
    messageId = client.put(_SERVER_IP, _SERVER_PORT, "test",
                                   _COAP_AUT_PASS,
                                   coap_macros.COAP_CONTENT_FORMAT.COAP_TEXT_PLAIN)
    print("[PUT] Message Id: ", messageId)


#Coap GET Message function.
def sendGetRequest(client):
    messageId = client.get(_SERVER_IP, _SERVER_PORT, _COAP_GET_REQ_URL)
    print("[GET] Message Id: ", messageId)

#On message callback. Called each time when message that is not ACK is received.
def receivedMessageCallback(packet, sender):
    print('Message received:', packet.toString(), ', from: ', sender)
    print('Packet info received:', packet.messageid, ', from: ', sender)
    #print('hello world:', packet.messageid,
    
    #Process the message content here. TADA

#Creates JSON from the available peripherals
def createJSON():
    json_string={"Lux":sensor.getLux()}
    json = ujson.dumps(json_string)
    return json


#Initialize  wifi handler
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
    
# print Wi-Fi Scan of APs around
aps_scan = wlan.scan() # store last Wi-Fi AP scan
countAPs = len(aps_scan) # get number of APs found

wlan.connect("LPWAN-IoT-04", "LPWAN-IoT-04-WiFi")

# while Wi-Fi is not connected
while not wlan.isconnected():
    
    print("WIFI STATUS CONNECTED: " + str(wlan.isconnected())) # print current status aka False=Not connect, True=Connected
    time.sleep_ms(500) # check period set to 500 ms

print("Wifi connected with configuration:")
print(wlan.ifconfig())

#Create a CoAP client
client = microcoapy.Coap()
client.debug = True

#Set the callback function for the message reception
client.responseCallback = receivedMessageCallback

# Starting CoAP client
client.start()

#Time variables and period definition
ticks_start = time.ticks_ms()
get_ticks_start = time.ticks_ms()
get_period = 6500
send_period = 5000#ms

#Send get request to get the initial state of the LED
sendGetRequest(client)


# Button interrupt
BUTTON1.irq(trigger=Pin.IRQ_FALLING, handler=pinPressedCallback)

    
while 1:
    time.sleep(1)
    
    # Get the intensity and display it
    lux = sensor.getLux()
    print(lux)
    
    # Display intesity on ledbar - max ledbar at lx > 9000
    level = lux/1000
    ledbar.level(level)
    
    # Check SD card
    with open("/sd/lux.txt", "r") as file:
        data = file.read()
        print("\n"+data+"\n")
    
    # Send intensity via CoAP
    if (time.ticks_diff(time.ticks_ms(), ticks_start) >= send_period):
        ticks_start=time.ticks_ms()
        json = createJSON()
        sendPostRequest(client, json)
        client.poll(10000, pollPeriodMs=1)
    
    
#Stop the client --- Should never get here.
client.stop()
        