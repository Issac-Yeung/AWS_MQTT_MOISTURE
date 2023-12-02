import time
import json
from machine import ADC, Pin, Timer
from umqtt.robust import MQTTClient
from Sensor import Sensor
from micropython import const

# Initialize ADC and MQTT client
KEY_PATH = const("AWS-IY-private.pem.key")
CERT_PATH = const("AWS-IY-certificate.pem.crt")
CLIENT_ID = const("AWS-IOT-CORE")
HOST = const("a30rplcugc3t7k-ats.iot.us-east-1.amazonaws.com")
PORT = const(8883)
AWS_PUBLISH = "$aws/things/Firebeetle/shadow/update"
AWS_GET = "$aws/things/Firebeetle/shadow/get"

def setup_AWS_SSL():
    try:
        with open(KEY_PATH, "r") as f:
            key = f.read()
        with open(CERT_PATH, "r") as f:
            cert = f.read()
        SSL_PARAMS = {"key":key, "cert":cert,"server_side":False}
        return SSL_PARAMS
    except Exception as e:
        print("Read SSL Certs Error", e)
    
try:
    mySensor = Sensor()
except Exception as e:
    print("Initial Sensor Error:", e)

try:
    SSL_PARAMS = setup_AWS_SSL()
    global client
    client = MQTTClient(client_id=CLIENT_ID,
                        server=HOST,
                        port=PORT,
                        keepalive=10000,
                        ssl=True,
                        ssl_params=SSL_PARAMS)
    client.connect()
    print("AWS connected")
except Exception as e:
    print("Setup MQTT Error:", e)

# do_readMoisture - Read Moisture and publish to MQTT
def do_readMoisture(tmrObj):
    try:
        data = mySensor.moisture()
        print(data)
        rawData = {
            "state":{
                "reported":{
                    "Raw": data["Raw"],
                    "Percent": data["Percent"],
                    "Volts": data["Volts"],
                    "DateTime": data["DateTime"]
                }
            }
        }

        client.publish(AWS_PUBLISH, json.dumps(rawData))
        print("Published data")
    except Exception as e:
        print("Read moisture/publish mqtt Error:", e)

# Use Machine Clock to trigger
tmr = Timer(-1)
tmr.init(mode=Timer.PERIODIC, period=10000, callback=do_readMoisture)
