import board
import busio
import adafruit_ahtx0
from logger import log


I2C0_SDA = board.GP8
I2C0_SCL = board.GP9
I2C1_SDA = board.GP26
I2C1_SCL = board.GP27


def set_up_sensors():
    sensor1 = sensor2 = None

    try:
        i2c0 = busio.I2C(I2C0_SCL, I2C0_SDA)
        sensor1 = adafruit_ahtx0.AHTx0(i2c0)
        log("Sensor1 (AHT) initialized on I2C0")
    except Exception as e:
        log(f"I2C0 init failed: {e}")
        sensor1 = None

    try:
        i2c1 = busio.I2C(I2C1_SCL, I2C1_SDA)
        sensor2 = adafruit_ahtx0.AHTx0(i2c1)
        log("Sensor2 (AHT) initialized on I2C1")
    except Exception as e:
        log(f"I2C1 init failed: {e}")
        sensor2 = None

    return sensor1, sensor2


def read_sensors(sensor1, sensor2):
    temp1 = hum1 = temp2 = hum2 = None

    if sensor1:
        try:
            temp1 = sensor1.temperature
            hum1 = sensor1.relative_humidity
        except Exception as e:
            log(f"Sensor1 (AHT) read error: {e}")

    if sensor2:
        try:
            temp2 = sensor2.temperature   
            hum2 = sensor2.relative_humidity
        except Exception as e:
            log(f"Sensor2 (AHT) read error: {e}")

    return temp1, hum1, temp2, hum2
