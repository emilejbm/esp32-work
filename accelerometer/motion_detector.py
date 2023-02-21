import MPU
import network
import esp32
import socket
import urequests
import ujson
import time
from machine import Timer, Pin, I2C
from neopixel import NeoPixel


i2c = I2C(scl=Pin(14), sda=Pin(22), freq=400000)
print(i2c)
mpu = MPU.MPU(i2c)

def test_accel():
    acc_x, acc_y, acc_z = mpu.acceleration() 
    print("Acceleration: X: %.2f, Y: %.2f, Z: %.2f m/s^2"%(mpu.acceleration()))
    #print("Gyro X:%.2f, Y: %.2f, Z: %.2f degrees/s"%(mpu.gyro))
    print("---------------------------------------")
    time.sleep(1)
    
    
ir0 = 0

# NeoPixel config
neo_pin = Pin(0, Pin.OUT)
neo_power_pin = Pin(2, Pin.OUT)
neo_power_pin.value(0)
np = NeoPixel(neo_pin, 8)

# Red LED config
red_led = Pin(13, Pin.OUT)
red_led.value(0)

# Calibrated MPU X,Y,Z values
ini_x = 0
ini_y = 0
ini_z = 0

def calibrate_accel():
    print('Calibrating accelerometer')
    global ini_x, ini_y, ini_z
    for i in range(100):
        j = i + 1
        new_x, new_y, new_z = mpu.acceleration()

        ini_x += new_x / j
        ini_y += new_y / j
        ini_z += new_z / j
        
    print('Done calibrating. Initial acceleromter values are x: {}, y: {}, z: {}'.format(ini_x, ini_y, ini_z))

def connect():
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        try:
            print('connecting to network...')
            sta_if.active(True)
            sta_if.connect('Emile iPhone', 'password12345')
        except:
            print('already connected')
            
        while not sta_if.isconnected():
            pass

    print('Connected to', 'Hotspot')
    print('IP Address:', sta_if.ifconfig())
    
    
connect()
calibrate_accel()


def readData(tim0):
    global ir0
    ir0 += 1
    

tim0 = Timer(0)
tim0.init(mode=Timer.PERIODIC, period=5000, callback=readData)
notified = False

while True:
    
    if ir0 > 0:
        notified = False
        ir0 -= 1
        
        #check if motion detection is activated
        response = urequests.get('https://api.thingspeak.com/channels/1976190/fields/1.json?api_key=7XFIDBQ86NJOD7VD&results=2')
        if response.json()['feeds'][-1]['field1'] == 'ACTIVATE':
            # turn NeoPixel on and detect acceleration
            
            print('checking MPU acceleration')
            
            neo_power_pin.value(1)
            np[0] = (0,255,0)
            np.write()
            
            while response.json()['feeds'][-1]['field1'] == 'ACTIVATE':
                acc_x, acc_y, acc_z = mpu.acceleration()
                
                # if motion is detected -> turn red led on and send notification to phone
                if ((abs(acc_x)-ini_x) > 1.0 or (abs(acc_y)-ini_y) > 1.0 or (abs(acc_z)-ini_z) > 1.0):
                    red_led.value(1)
                    
                    if notified is False:
                        accel_data = ujson.dumps({ 'x accel': acc_x, 'y accel': acc_y, 'z accel': acc_z})
                        res = urequests.post(url="https://maker.ifttt.com/trigger/motion_detected/json/with/key/d3OTBD4TtUAwq35ETJaA27", headers={"Content-Type": "application/json"}, data=accel_data)
                        
                        print(res.content)
                        res.close()
                        notified = True
                else:
                    red_led.value(0)
            
                response = urequests.get('https://api.thingspeak.com/channels/1976190/fields/1.json?api_key=7XFIDBQ86NJOD7VD&results=2')
                if response.json()['feeds'][-1]['field1'] == 'DEACTIVATE':
                    neo_power_pin.value(0)
                    np[0] = (0,0,0)
                    np.write()
                    break

        else:
            neo_power_pin.value(0)
            np[0] = (0,0,0)
            np.write()
        response.close()
