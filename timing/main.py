import network
import time
import ntptime
import machine
from machine import Timer, Pin, TouchPad
from neopixel import NeoPixel
import esp32

if machine.wake_reason() == machine.DEEPSLEEP_RESET or machine.wake_reason() == machine.DEEPSLEEP:
    print('Woke up due to timer')
elif machine.wake_reason() == machine.PIN_WAKE:
    print('Woke up due to EXT0 wakeup.')
    

ir1 = 0
ir2 = 0
ir3 = 0
ir4 = 0

#input GPIO for wake-up
wake_pin = Pin(15, Pin.IN)
#wake_pin.irq(trigger=Pin.IRQ_RISING, handler=checkPress)


#touch enabled pin
tch_pin = TouchPad(Pin(32))

#NeoPixel config
neo_pin = Pin(0, Pin.OUT)
neo_power_pin = Pin(2, Pin.OUT)
neo_power_pin.value(0)
np = NeoPixel(neo_pin, 8)

#Red LED
led = Pin(13, Pin.OUT)
led = led.value(1)


def connect():
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect('Rise Guest')
        while not sta_if.isconnected():
            pass
    
    print('Connected to', 'Rise Guest')
    print('IP Address:', sta_if.ifconfig())
    

connect()


ntptime.host='pool.ntp.org'
ntptime.settime()
UTC_OFFSET = -4 * 60 * 60
rtc = machine.RTC()
#rtc.datetime(time.localtime(time.time() + UTC_OFFSET))
rtc.datetime(time.localtime())
#print(rtc.datetime())

    
def displayTime(tim1):
    global ir1
    ir1 += 1
    
def checkTouchPin(tim2):
    #print(tch_pin.read())
    global ir2
    ir2 += 1

def goSleep(tim3):
    global ir4
    ir4 += 1
    
def checkPress():
    global ir3
    ir3 += 1
        

tim1 = Timer(0)
tim1.init(mode=Timer.PERIODIC, period=15000, callback=displayTime)

#read touch pin
tim2 = Timer(1)
tim2.init(mode=Timer.PERIODIC, period=50, callback=checkTouchPin)

tim3 = Timer(2)
tim3.init(mode=Timer.PERIODIC, period=30000, callback=goSleep)

esp32.wake_on_ext0(wake_pin, esp32.WAKEUP_ANY_HIGH)

while(True):
    #check time
    if(ir1 > 0):
        ir1 -= 1
        currTime = rtc.datetime()
        hour = 0
        print('local time', time.localtime())
        if currTime[3] >= 0 and currTime[3] < 4:
            hour = currTime[3] + 24 - 4
        else:
            hour = currTime[3] - 4
        print('Date: ', currTime[1], '/', currTime[2], '/', currTime[0])
        print('Time: ', hour, ':', currTime[4], ':', currTime[5], ' HRS')
        
        
    if(ir2 > 0):
        ir2 -= 1
        if tch_pin.read() > 900:
            #not touched: neo pixel should be off
            neo_power_pin.value(0)
            np[0] = (0,0,0)
            np.write()
        else:
            #touched: neo pixel should be ON and lit GREEN
            neo_power_pin.value(1)
            np[0] = (0,255,0)
            np.write()
            
        
    #button press
    if(ir3 > 0):
        ir3 -= 1
        
        
    #go sleep
    if(ir4 > 0):
        ir4 -= 1
        print('I am going to sleep for 1 minute.')
        machine.deepsleep(60000)
        

