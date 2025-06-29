import time
import board
import busio
import adafruit_ahtx0
import wifi
import socketpool
import adafruit_minimqtt.adafruit_minimqtt as MQTT


# MQTT broker details
MQTT_BROKER = "YOUR_MQTT_BROKER_ADDRESS"
MQTT_PORT = 1883
MQTT_TOPIC = "sensor/data"

# Unique identifier for this Pico W
SENSOR_ID = "PICO_W_01"

# Connect to Wi-Fi
print("Connecting to Wi-Fi...")
wifi.radio.connect(wifi.radio.ssid, wifi.radio.password)
print("Connected!")

# Set up I2C and two AHT21 sensors
i2c = busio.I2C(board.GP1, board.GP0)  # Adjust pins as needed

# Sensor 1 at default address 0x38
sensor1 = adafruit_ahtx0.AHTx0(i2c, address=0x38)
# Sensor 2 at alternate address 0x39
sensor2 = adafruit_ahtx0.AHTx0(i2c, address=0x39)

# Set up MQTT client
pool = socketpool.SocketPool(wifi.radio)
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
    timestamp = time.time()  # seconds since boot

    # Prepare payload
    payload = (
        f"{SENSOR_ID},{timestamp:.0f},{temp1:.2f},{hum1:.2f},{temp2:.2f},{hum2:.2f}"
    )

    # Publish to MQTT
    print(f"Publishing: {payload}")
    mqtt_client.publish(MQTT_TOPIC, payload)

    time.sleep(10)  # Adjust interval as needed
