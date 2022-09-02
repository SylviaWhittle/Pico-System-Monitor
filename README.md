# Pico-System-Monitor
A Raspberry Pi Pico W based system monitor using OpenHardwareMonitor and Wifi. 


I developed this for my Windows system as Task Manager doesn't have a dark theme, and it takes up screen space that I need.
The stats are acquired using Open Hardware Monitor https://openhardwaremonitor.org/, and are then sent in HTTP requests to a Pico W on the same network. I use a Pimoroni Pico Enviro + as the screen for it since I like to be able to have room ambient temperature information alongside my hardware stats. If you are using another display, then you will need to change any code relating to the displaying of data to accomodate for that. 

You will need to list your network's SSID and password in a text file called `secrets.txt` in the same directory as the code. Eg: 
SSID = "myNetwork"
PASSWORD = "securePassword"

## Security
The data is completely unencrypted and uses bare HTTP requests rather than HTTPS, so only use this on your private, local networks. 
