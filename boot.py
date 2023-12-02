import time
import network
import webrepl
from ntptime import settime

# do_connect() - Connect to WIFI
def do_connect():
    try:
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        print('Connecting to network...')
        while not wlan.isconnected():
            wlan.connect('BELL168_EXT', '1AD1EC2F5D51')
            time.sleep(5)
        print('Network config:', wlan.ifconfig())
    except Exception as e:
        print ("boot.do_connect Error: ", e)

def format_time(t):
    return "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(*t[0:6])

try:
    # Connect WIFI
    do_connect()
    # Display current time
    settime()
    now = time.time()
    current_time = format_time(time.localtime(now - 21600))
    print("System time: ", current_time)
    webrepl.start()
except Exception as e:
    print ("boot.Exception: ", e)