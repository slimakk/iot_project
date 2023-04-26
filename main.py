from machine import Pin, I2C
from TMG3993 import *
from my9221 import MY9221
import time
import network
import ujson
import microcoapy
import coap_macros

#CoAP server key information
_SERVER_IP ='86.49.182.194'
_SERVER_PORT = 36105  #5683 36105 default CoAP port
_COAP_POST_URL = 'api/v1/IoT_08/telemetry' # fill your Device name, select based on your workstation
_COAP_GET_REQ_URL = 'api/v1/IoT_08/attributes' # fill your Device name, select based on your workstation
_COAP_AUT_PASS = 'authorization=IoT_99' # fill your Device name, select based on your workstation

i2c = I2C(0, scl=Pin(5), sda=Pin(4), freq=400000)

print(i2c.scan())

sensor = TMG3993(i2c)

ledbar = MY9221(di=Pin(3), dcki=Pin(2))

print(sensor.getDeviceID())

sensor.enableEngines(0x01 | 0x02 | 0x10)

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

#Connect to WiFi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect("LPWAN-IoT-08", "LPWAN-IoT-08-WiFi")


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
send_period = 1500#ms

#Send get request to get the initial state of the LED
sendGetRequest(client)



    
while 1:
    time.sleep(1)
    lux = sensor.getLux()
    print(lux)
    level = lux/1000
    ledbar.level(level)
    if (time.ticks_diff(time.ticks_ms(), ticks_start) >= send_period):
        ticks_start=time.ticks_ms()
        json = createJSON()
        sendPostRequest(client, json)
      
    #Get the LED state from the server periodically
    #if (time.ticks_diff(time.ticks_ms(), get_ticks_start) >= get_period):
    #    get_ticks_start = time.ticks_ms()
    #    sendGetRequest(client)
    
    #Let the client do it's thing - send and receive CoAP messages.
    client.poll(10000, pollPeriodMs=1)
    
#Stop the client --- Should never get here.
client.stop()
        