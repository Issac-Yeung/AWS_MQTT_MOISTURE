import time
from machine import ADC, Pin

# Initialize ADC and MQTT client
class Sensor:
    # Constructor
    def __init__(self):
        try:
            self.adc = ADC(Pin(36))
            self.adc.atten(ADC.ATTN_11DB)
        except Exception as e:
            print("init Exception: ", e)
    # format time
    def format_time(self, t):
        return "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(*t[0:6])
    # moisture() - read time
    def moisture(self):
        try:
            now = time.time()
            current_time = self.format_time(time.localtime(now - 21600))
            raw = self.adc.read()
            print(raw)
            data = {
                "Raw": raw,
                "Percent": 100 - (100 * raw / 4095),
                "Volts": 3.3 * raw / 4095,
                "DateTime": current_time
            }
            return data
        except Exception as e:
            print("moisture Exception: ", e)
