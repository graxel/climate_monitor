import os
import wifi
import ssl
import rtc
import adafruit_requests
from logger import log

def set_up_wifi():
    ssid = os.getenv("CIRCUITPY_WIFI_SSID")
    password = os.getenv("CIRCUITPY_WIFI_PASSWORD")
    log("Connecting to Wi-Fi...")
    wifi.radio.connect(ssid, password)
    log("Connected!")
    return wifi.radio

def set_rtc_from_net(radio):
    pool = getattr(radio, 'socket_pool', None) or __import__('socketpool').SocketPool(radio)
    requests = adafruit_requests.Session(pool, ssl.create_default_context())
    response = requests.get("http://worldtimeapi.org/api/ip")
    data = response.json()
    struct_time = __import__('time').localtime(data["unixtime"])
    rtc.RTC().datetime = struct_time
    log("RTC set!")