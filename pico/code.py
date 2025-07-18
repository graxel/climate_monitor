from networking import set_up_wifi, set_rtc_from_net
from sensors import set_up_sensors, read_sensors, set_up_switch
from mqtt_manager import MqttManager
import time
from logger import log

import microcontroller
from watchdog import WatchDogMode


# --- Watchdog setup ---
microcontroller.watchdog.timeout = 8
microcontroller.watchdog.mode = WatchDogMode.RESET
microcontroller.watchdog.feed()


switch = set_up_switch()
radio = set_up_wifi()
set_rtc_from_net(radio)
sensor1, sensor2 = set_up_sensors()
mqtt = MqttManager(radio)

while True:
    try:
        microcontroller.watchdog.feed()
        mqtt.loop()

        temp1, hum1, temp2, hum2 = read_sensors(sensor1, sensor2)
        timestamp = time.mktime(time.localtime())
        payload = f"{mqtt.sensor_id},{timestamp},{temp1:.2f},{hum1:.2f},{temp2:.2f},{hum2:.2f}"
        log(f"Publishing: {payload}")
        mqtt.publish(payload)

        microcontroller.watchdog.feed()

    except Exception as e:
        log("Exception in main loop:", e)
        mqtt.recover()

    if switch.value:
        time.sleep(1)
    else:
        time.sleep(3)
    microcontroller.watchdog.feed()