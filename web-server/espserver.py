from machine import Pin
import network, esp32, gc

# Global variables
temp = esp32.raw_temperature()# measure temperature sensor data
hall = esp32.hall_sensor() # measure hall sensor data
red_led_state = "OFF" # string, check state of red led, ON or OFF
red_led = Pin(13, Pin.OUT)
sta_if = 0

try:
  import usocket as socket
except:
  import socket


gc.collect()


def connect():
    global sta_if
    sta_if = network.WLAN(network.STA_IF)
    while not sta_if.isconnected():
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

def web_page():
    temp = esp32.raw_temperature()
    hall = esp32.hall_sensor()
    temp_str = str(temp)
    hall_str = str(hall)
    
    if red_led.value() == 1:
        red_led_state="ON"
    else:
        red_led_state="OFF"
    
    """Function to build the HTML webpage which should be displayed
    in client (web browser on PC or phone) when the client sends a request
    the ESP32 server.
    
    The server should send necessary header information to the client
    (YOU HAVE TO FIND OUT WHAT HEADER YOUR SERVER NEEDS TO SEND)
    and then only send the HTML webpage to the client.
    
    Global variables:
    temp, hall, red_led_state
    """
    
    html_webpage = """<!DOCTYPE HTML><html>
    <head>
    <title>ESP32 Web Server</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.7.2/css/all.css" integrity="sha384-fnmOCqbTlWIlj8LyTjo7mOUStjsKC4pOpQbqyi7RrhN7udi9RwhKkMHpvLbHG9Sr" crossorigin="anonymous">
    <style>
    html {
     font-family: Arial;
     display: inline-block;
     margin: 0px auto;
     text-align: center;
    }
    h1 { font-size: 3.0rem; }
    p { font-size: 3.0rem; }
    .units { font-size: 1.5rem; }
    .sensor-labels{
      font-size: 1.5rem;
      vertical-align:middle;
      padding-bottom: 15px;
    }
    .button {
        display: inline-block; background-color: #e7bd3b; border: none; 
        border-radius: 4px; color: white; padding: 16px 40px; text-decoration: none;
        font-size: 30px; margin: 2px; cursor: pointer;
    }
    .button2 {
        background-color: #4286f4;
    }
    </style>
    </head>
    <body>
    <h1>ESP32 WEB Server</h1>
    <p>
    <i class="fas fa-thermometer-half" style="color:#059e8a;"></i> 
    <span class="sensor-labels">Temperature</span> 
    <span>"""+str(temp)+"""</span>
    <sup class="units">&deg;F</sup>
    </p>
    <p>
    <i class="fas fa-bolt" style="color:#00add6;"></i>
    <span class="sensor-labels">Hall</span>
    <span>"""+str(hall)+"""</span>
    <sup class="units">V</sup>
    </p>
    <p>
    RED LED Current State: <strong>""" + red_led_state + """</strong>
    </p>
    <p>
    <a href="/?red_led=on"><button class="button">RED ON</button></a>
    </p>
    <p>
    <a href="/?red_led=off"><button class="button button2">RED OFF</button></a>
    </p>
    </body>
    </html>"""
    return html_webpage


addr = socket.getaddrinfo((sta_if.ifconfig()[0]), 80)[0][-1]
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(addr)
s.listen(5)

print(addr)

while True:
    conn, addr = s.accept()
    print('Got a connection from %s' % str(addr))
    request = str(conn.recv(1024))
    
    print('Content = %s' % request)
    led_state_on = request.find('/?red_led=on')
    led_state_off = request.find('/?red_led=off')
    
    if led_state_on == 6:
        print('LED ON')
        red_led.value(1)
    if led_state_off == 6:
        print('LED OFF')
        red_led.value(0)
        
    response = web_page()
    conn.send('HTTP/1.1 200 OK\n')
    conn.send('Content-Type: text/html\n')
    conn.send('Connection: close\n\n')
    conn.sendall(response)
    conn.close()


