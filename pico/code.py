import os
import time
import board
import busio
import adafruit_ahtx0
import wifi
import socketpool
import adafruit_minimqtt.adafruit_minimqtt as MQTT


# wifi creds from settings.toml
ssid = os.getenv("CIRCUITPY_WIFI_SSID")
password = os.getenv("CIRCUITPY_WIFI_PASSWORD")

# MQTT broker details
MQTT_BROKER = os.getenv("MQTT_BROKER_ADDRESS")
MQTT_PORT = 1883
MQTT_TOPIC = "sensor/data"

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

# # Set up MQTT client
# pool = socketpool.SocketPool(wifi.radio)
# mqtt_client = MQTT.MQTT(
#     broker=MQTT_BROKER,
#     port=MQTT_PORT,
#     socket_pool=pool,
# )

# def connect(client, userdata, flags, rc):
#     print("Connected to MQTT broker!")

# mqtt_client.on_connect = connect
# mqtt_client.connect()

while True:
    # Read data from both sensors
    temp1 = sensor1.temperature
    hum1 = sensor1.relative_humidity
    temp2 = sensor2.temperature
    hum2 = sensor2.relative_humidity
    timestamp = time.time()  # seconds since boot

    # Prepare payload
    payload = (
        f"{SENSOR_ID},{timestamp:.0f},{temp1:.2f},{hum1:.2f},{temp2:.2f},{hum2:.2f}"
    )

    # Publish to MQTT
    print(f"Publishing: {payload}")
    # mqtt_client.publish(MQTT_TOPIC, payload)

    time.sleep(1)  # Adjust interval as needed
