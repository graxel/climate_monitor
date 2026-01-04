import board
import busio
import adafruit_ahtx0
import adafruit_ens160
from logger import log


I2C0_SDA = board.GP20
I2C0_SCL = board.GP21
I2C1_SDA = board.GP10
I2C1_SCL = board.GP11


def set_up_sensors():
    sensor1 = sensor2 = sensor3 = None
    i2c0 = i2c1 = None

    try:
        i2c0 = busio.I2C(I2C0_SCL, I2C0_SDA)
        sensor1 = adafruit_ahtx0.AHTx0(i2c0)
        sensor3 = adafruit_ens160.ENS160(i2c0)
        log("Sensor1 (AHT) + Sensor3 (ENS160) initialized on I2C0")
    except Exception as e:
        log(f"I2C0 / Sensor1+3 (AHT+ENS160) init failed: {e}")
        sensor1 = None
        sensor3 = None

    try:
        i2c1 = busio.I2C(I2C1_SCL, I2C1_SDA)
        sensor2 = adafruit_ahtx0.AHTx0(i2c1)
        log("Sensor2 (AHT) initialized on I2C1")
    except Exception as e:
        log(f"I2C1 / Sensor2 (AHT) init failed: {e}")
        sensor2 = None

    return sensor1, sensor2, sensor3, i2c0, i2c1


def read_sensors(sensor1, sensor2, sensor3, i2c0, i2c1):
    temp1 = hum1 = temp2 = hum2 = None
    co2 = aqi = None

    if sensor1 and i2c0:
        try:
            if i2c0.try_lock():
                temp1 = sensor1.temperature
                hum1 = sensor1.relative_humidity
                i2c0.unlock()
        except Exception as e:
            log(f"Sensor1 (AHT) read error: {e}")

    if sensor2 and i2c1:
        try:
            if i2c1.try_lock():
                temp2 = sensor2.temperature
                hum2 = sensor2.relative_humidity
                i2c1.unlock()
        except Exception as e:
            log(f"Sensor2 (AHT) read error: {e}")

    if sensor3 and i2c0:
        try:
            if i2c0.try_lock():
                co2 = sensor3.eCO2
                aqi = sensor3.AQI
                i2c0.unlock()
        except Exception as e:
            log(f"Sensor3 (ENS160) read error: {e}")

    return temp1, hum1, temp2, hum2, co2, aqi

