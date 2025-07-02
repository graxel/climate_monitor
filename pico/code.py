import os
import ssl
import rtc
import wifi
import time
import board
import busio
import digitalio
import socketpool
import adafruit_ahtx0
import adafruit_datetime
import adafruit_requests
import adafruit_minimqtt.adafruit_minimqtt as MQTT

# Set up switch on GP15 with pull-up
switch = digitalio.DigitalInOut(board.GP15)
switch.direction = digitalio.Direction.INPUT
switch.pull = digitalio.Pull.UP  # Pull-up resistor enabled

# wifi creds from settings.toml
ssid = os.getenv("CIRCUITPY_WIFI_SSID")
password = os.getenv("CIRCUITPY_WIFI_PASSWORD")

# MQTT broker details
MQTT_BROKER = os.getenv("MQTT_BROKER_ADDRESS")
MQTT_PORT = int(os.getenv("MQTT_PORT"))
MQTT_TOPIC = os.getenv("MQTT_TOPIC")

# Unique identifier for this Pico W
SENSOR_ID = "PICO_W_01"

# Connect to Wi-Fi
print("Connecting to Wi-Fi...")
wifi.radio.connect(ssid, password)
print("Connected!")

# I2C0 on GPIO 0 (SDA), GPIO 1 (SCL)
i2c0 = busio.I2C(board.GP1, board.GP0)
sensor1 = adafruit_ahtx0.AHTx0(i2c0)

# I2C1 on GPIO 2 (SDA), GPIO 3 (SCL)
i2c1 = busio.I2C(board.GP3, board.GP2)
sensor2 = adafruit_ahtx0.AHTx0(i2c1)

pool = socketpool.SocketPool(wifi.radio)

# Fetch time from WorldTimeAPI
requests = adafruit_requests.Session(pool, ssl.create_default_context())
response = requests.get("http://worldtimeapi.org/api/ip")
data = response.json()
datetime_str = data["datetime"]
dt = adafruit_datetime.datetime.fromisoformat(datetime_str)

# Convert to struct_time for RTC
struct_time = time.struct_time((
    dt.year, dt.month, dt.day,
    dt.hour, dt.minute, dt.second,
    dt.weekday(), -1, -1
))

# Set the RTC
rtc.RTC().datetime = struct_time
print("RTC set!")


# Set up MQTT client
mqtt_client = MQTT.MQTT(
    broker=MQTT_BROKER,
    port=MQTT_PORT,
    socket_pool=pool,
)

def connect(client, userdata, flags, rc):
    print("Connected to MQTT broker!")

mqtt_client.on_connect = connect
mqtt_client.connect()


while True:
    # Read data from both sensors
    temp1 = sensor1.temperature
    hum1 = sensor1.relative_humidity
    temp2 = sensor2.temperature
    hum2 = sensor2.relative_humidity
    timestamp = time.mktime(time.localtime())

    # Prepare payload
    payload = (
        f"{SENSOR_ID},{timestamp},{temp1:.2f},{hum1:.2f},{temp2:.2f},{hum2:.2f}"
    )

    # Publish to MQTT
    print(f"Publishing: {payload}")
    mqtt_client.publish(MQTT_TOPIC, payload)

    if switch.value: # if switch is closed, report more frequently
        time.sleep(1)
    else:
        time.sleep(3)

