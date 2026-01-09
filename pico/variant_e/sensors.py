import board
import busio
import adafruit_ahtx0
from logger import log

I2C1_SDA = board.GP6
I2C1_SCL = board.GP7


def set_up_sensors():
    sensor1 = None

    try:
        i2c1 = busio.I2C(I2C1_SCL, I2C1_SDA)
        sensor1 = adafruit_ahtx0.AHTx0(i2c1)
        log("Sensor1 (AHT) initialized on I2C1")
    except Exception as e:
        log(f"I2C1 init failed: {e}")
        sensor1 = None

    return sensor1


def read_sensors(sensor1):
    temp1 = hum1 = None

    if sensor1:
        try:
            temp1 = sensor1.temperature
            hum1 = sensor1.relative_humidity
        except Exception as e:
            log(f"Sensor1 (AHT) read error: {e}")

    return temp1, hum1
