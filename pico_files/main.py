import network
import secrets
import time
import machine
from machine import Pin, UART
import socket
from picographics import PicoGraphics, DISPLAY_ENVIRO_PLUS
from pimoroni import RGBLED, Button
import re

import _thread

# Sensors from the board
# from breakout_bme68x import BreakoutBME68X, STATUS_HEATER_STABLE
# from pimoroni_i2c import PimoroniI2C
# from breakout_ltr559 import BreakoutLTR559
# from adcfft import ADCFFT

# set up the display
display = PicoGraphics(display=DISPLAY_ENVIRO_PLUS, rotate=90)

# set up the buttons
button_a = Button(12, invert=True)
button_b = Button(13, invert=True)
button_x = Button(14, invert=True)
button_y = Button(15, invert=True)

# Configure LED and Buttons
led = RGBLED(6, 7, 10, invert=True) # pins that it uses
led.set_rgb(50, 50, 50)
button_a = Button(12, invert=True)  # (button, invert, repeat_time, hold_time) 
button_b = Button(13, invert=True)  # button seems to be the pin on which they direct to
button_x = Button(14, invert=True)
button_y = Button(15, invert=True)

WHITE = display.create_pen(255, 255, 255)
BLACK = display.create_pen(0, 0, 0)
COL_BOX = display.create_pen(160, 160, 200)
COL_CPU = display.create_pen(255, 120, 240)
COL_RAM = display.create_pen(255, 120, 190)
COL_GPU = display.create_pen(229, 120, 80)
COL_RAM_LT = COL_RAM
COL_GPU_LT = COL_GPU
RED = display.create_pen(255, 0, 0)
CYAN = display.create_pen(0, 255, 255)
COL_CPU_LT = COL_CPU
YELLOW = display.create_pen(200, 200, 0)
BLUE = display.create_pen(0, 0, 200)
FFT_COLOUR = display.create_pen(255, 0, 255)
GREY = display.create_pen(100, 100, 100)

WIDTH, HEIGHT = display.get_bounds()
display.set_font("bitmap8")

display.set_pen(WHITE)
display.text("initializing . . .", round(WIDTH/4), round(HEIGHT/2), scale=1.5) # text, x, y, wordwrap, scale, angle, spacing
display.update()
time.sleep(1)

html_start = """<!DOCTYPE html>
    <html>
        <head> <title>Pico W</title> </head>
        <body> <h1>Pico W</h1>
            <p>Hello World</p>
            <p>
            <a href='/light/on'>Turn Light On</a>
            </p>
            <p>
            <a href='/light/off'>Turn Light Off</a>
            </p>
            <br>
            
            <canvas id="myCanvas" width="200" height="100" style="border:1px solid #d3d3d3;">
Your browser does not support the HTML canvas tag.</canvas>
"""

# html_script = """
#         <script>
#         var c = document.getElementById("myCanvas");
#         var ctx = c.getContext("2d");
#         ctx.moveTo(0,0);
#         ctx.lineTo(200,100);
#         ctx.stroke();
#         </script>
# """

html_end = """
        </body>
    </html>
"""

global data
data = {
    "CPU_temp": None,
    "RAM_used": None,
    "CPU_load_total": None,
    "RAM_load": None,
    "GPU_load": None,
    "GPU_RAM_load": None,
    "GPU_RAM_used": None,
    "GPU_RAM_total": None,
    "GPU_temperature": None,
    "C_drive_load": None,
    "D_drive_load": None
}

# Display functions
def display_clear():
    display.set_pen(BLACK)
    display.clear()
    
def write(text, x, y, scale=2):
    display.text(text, x, y, scale=scale)
    
def graph_bar(value, width, x, y, color=WHITE):
    bhl = 20
    bhs = 4
    bw = 5
    spacing = 8
    display.set_pen(color)
    scaled_value = int(width/100 * value)
    for i in range(width):
        if i < scaled_value:
            if i % spacing == 0:
                display.rectangle(x + i, y, bw, bhl)
        else:
            if i % spacing == 0:
                display.rectangle(x + i, y+round((bhl-bhs)/2), bw, bhs)


def thread_display():
    print('starting thread: display')
    global data
    global HEIGHT
    global WIDTH
    global secrets
    
    bar_width = WIDTH - 20
    
    time.sleep(2)
    while True:
        display_clear()
#         display.rectangle(CONSOLE_LEFT, CONSOLE_TOP, CONSOLE_WIDTH, CONSOLE_HEIGHT)
        
#         print(f'wlanstatus: {wlan.status()}')
        if wlan.status() == 3:
            display.set_pen(GREY)
            write(f'Connected to: {secrets.SSID}', 2, HEIGHT - 20, scale=2)
            led.set_rgb(0, 1, 0)
        else:
            display.set_pen(GREY)
            write(f'Disconnected', 2, HEIGHT - 20, scale=2)
            led.set_rgb(10, 0, 0)
        
#         i = int(HEIGHT/2)
#         for key, value in data.items():
#             write(f'{key}: {value}', int(WIDTH/2), i)
#             i += 12
        
        X = 1
        Y = 1
        display.set_pen(COL_BOX)
        display.rectangle(X, Y, 2, 38)
        display.rectangle(X, Y, WIDTH-1, 2)
        display.rectangle(WIDTH-2, Y, 2, 38)
        display.rectangle(X, Y+38, 16, 2)
        display.rectangle(WIDTH-87, Y+38, 87, 2)
        display.rectangle(X+16, Y+32, 2, 14)
        display.rectangle(WIDTH-87, Y+32, 2, 14)
        # Draw CPU usage
        if data['CPU_load_total'] != None:
            graph_bar(data['CPU_load_total'], bar_width, X+6, Y+6, color=COL_CPU)
            display.set_pen(COL_CPU_LT)
            write(f" CPU: {int(data['CPU_load_total'])}% ", X+16, Y+32)
            write(f"| {int(data['CPU_temp'])} C ", X+98, Y+32)
            
        X = 1
        Y = 54
        display.set_pen(COL_BOX)
        display.rectangle(X, Y, 2, 38)
        display.rectangle(X, Y, WIDTH-1, 2)
        display.rectangle(WIDTH-2, Y, 2, 40)
        display.rectangle(X, Y+38, 16, 2)
        display.rectangle(WIDTH-85, Y+38, 85, 2)
        display.rectangle(X+16, Y+32, 2, 14)
        display.rectangle(WIDTH-85, Y+32, 2, 14)
        display.set_pen(COL_RAM)
        if data['RAM_load'] != None:
            graph_bar(data['RAM_load'], bar_width, X+6, Y+6, color=COL_RAM)
            display.set_pen(COL_RAM_LT)
            write(f" RAM: {int(data['RAM_load'])}% ", X+16, Y+32)
            write(f"| {round(data['RAM_used'])}GB ", X+105, Y+32)
        
        X = 1
        Y = 107
        display.set_pen(COL_BOX)
        display.rectangle(X, Y, 2, 78)
        display.rectangle(X, Y, WIDTH-1, 2)
        display.rectangle(WIDTH-2, Y, 2, 78)
        display.rectangle(X, Y+38, 16, 2)
        display.rectangle(WIDTH-82, Y+38, 82, 2)
        display.rectangle(X, Y+78, 16, 2)
        display.rectangle(WIDTH-82, Y+78, 82, 2)
        display.rectangle(X+16, Y+30, 2, 14)
        display.rectangle(WIDTH-82, Y+32, 2, 14)
#         display.rectangle(WIDTH-140, Y+32, 2, 14)
        display.rectangle(X+16, Y+72, 2, 14)
        display.rectangle(WIDTH-82, Y+72, 2, 14)
        if data['GPU_load'] != None:
            graph_bar(data['GPU_load'], bar_width, X+6, Y+6, color=COL_GPU)
            display.set_pen(COL_GPU_LT)
            write(f" GPU: {int(data['GPU_load'])}% ", X+16, Y+32)
            write(f"| {round(data['GPU_temperature'])} C ", X+105, Y+32)
            graph_bar(data['GPU_RAM_load'], bar_width, X+6, Y+50, color=COL_GPU)
            display.set_pen(COL_GPU_LT)
            write(f" VRAM: {round(data['GPU_RAM_used']/1024)} / {round(data['GPU_RAM_total']/1024)} GB ", X+16, Y+74)
            
            
        
        print('display tick')
        display.update()
        time.sleep(1)

# establish network connection
success = False
if secrets.SSID != None and secrets.SSID != "":
    display_clear()
    write(f'attempting to connect...', 10, round(HEIGHT/2))
    write(f'SSID: {secrets.SSID}', 10, round(HEIGHT/2) + 20)
    display.update()
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(secrets.SSID, secrets.PASSWORD)
    
    # Wait for connect or fail
    max_wait = 10
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        print('waiting for connection...')
        time.sleep(1)
    
    print(f'wlan status: {wlan.status()}')
    if wlan.status() != 3:
        raise RuntimeError('network connection failed')
        success = False
    else:
        success = True
        print('connected')
        ifconfig = wlan.ifconfig()
        print(f'ifconfig: {ifconfig}')
        print(f'ip: {ifconfig[0]}')
    
    if success:
        led.set_rgb(0, 50, 0)
        display_clear()
        display.set_pen(WHITE)
        write(f'success!', round(WIDTH/2) - 40, round(HEIGHT/2))
        write(f'connected to: {secrets.SSID}', 10, round(HEIGHT/2 + 20))
        display.update()
        time.sleep(1)
    else:
        led.set_rgb(50, 0, 0)
        display_clear()
        write(f'connection failed', round(WIDTH/4) - 5, round(HEIGHT/2))
        display.update()
        time.sleep(2)

addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
print(f'addr: {addr}')
try:
    s = socket.socket()
except OSError as e:
    print(f'Error: {e}')
    time.sleep(1)
    machine.reset()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(addr)
s.listen(1)

stateis = ""

_thread.start_new_thread(thread_display, ())

# Listen for connections
while True:
    try:
        cl, addr = s.accept()
#         print(f'client connected from: {addr}')
        request = cl.recv(1024)
#         print(f'request: {request}')
        
        request = str(request)
        led_on = request.find('/light/on')
        led_off = request.find('/light/off')
        
        if led_on == 6:
            print('led on')
            led.set_rgb(100, 100, 100)
            stateis = "LED is on"
        if led_off == 6:
            print('led off')
            led.set_rgb(0, 0, 0)
            stateis = "LED is off"
        
        print('request received')
#         print(request)
        
        for key in data.keys():
            value = re.search(f"S{key}(.*?)E{key}", request)
            if value is not None:
                data[key] = float(value.group(1))
            
#         print('\n----------------------------------------')
#         print(data)
#         print('----------------------------------------\n')
        
#         cpu = re.search('stemp(.*?)etemp', request)
#         print(cpu.group(1))
        
        # Craft custom HTML response
        display_data = f"<br> display data here"
        response = html_start + stateis + html_end
        
        cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
        cl.send(response)
        cl.close()
    except OSError as e:
        cl.close()
        print('connection closed')
