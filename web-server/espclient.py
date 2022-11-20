import network
import esp32
import socket
from machine import Timer, Pin
import urequests
#from espserver import web_page

ir0 = 0

def connect():
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        try:
            print('connecting to network...')
            sta_if.active(True)
            sta_if.connect('Rise Guest')
        except:
            print('already connected')
            
        while not sta_if.isconnected():
            pass

    print('Connected to', 'Rise Guest')
    print('IP Address:', sta_if.ifconfig())
    

connect()

def publishData(tim0):
    global ir0
    ir0 += 1
    

tim0 = Timer(0)
tim0.init(mode=Timer.PERIODIC, period=30000, callback=publishData)


while True:
    
    if ir0 > 0:
        ir0 -= 1
        response = urequests.get('https://api.thingspeak.com/update?api_key=CCRRFFP9JEPPCLO5&field1=' + str(esp32.raw_temperature()) + '&field2=' + str(esp32.hall_sensor()))
        print(response)
        response.close()
        