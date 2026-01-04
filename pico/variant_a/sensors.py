import board
import busio
import adafruit_ahtx0
from logger import log


I2C0_SDA = board.GP0
I2C0_SCL = board.GP1
I2C1_SDA = board.GP2
I2C1_SCL = board.GP3

def set_up_sensors():
    try:
        i2c0 = busio.I2C(I2C0_SCL, I2C0_SDA)
        sensor1 = adafruit_ahtx0.AHTx0(i2c0)
        log("Sensor1 (AHT) initialized")
    except Exception as e:
        log(f"Sensor1 (AHT) failed: {e}")
        sensor1 = None
    
    try:
        i2c1 = busio.I2C(I2C1_SCL, I2C1_SDA)
        sensor2 = adafruit_ahtx0.AHTx0(i2c1)
        log("Sensor2 (AHT) initialized")
    except Exception as e:
        log(f"Sensor2 (AHT) failed: {e}")
        sensor2 = None
    
    return sensor1, sensor2, i2c0, i2c1


def read_sensors(sensor1, sensor2, i2c0, i2c1):
    temp1 = hum1 = temp2 = hum2 = None
    
    if sensor1:
        try:
            if i2c0.try_lock():
                temp1 = sensor1.temperature
                hum1 = sensor1.relative_humidity
                i2c0.unlock()
        except Exception as e:
            log(f"Sensor1 (AHT) read error: {e}")
    
    if sensor2:
        try:
            if i2c1.try_lock():
                temp2 = sensor2.temperature
                hum2 = sensor2.relative_humidity
                i2c1.unlock()
        except Exception as e:
            log(f"Sensor2 (AHT) read error: {e}")
    
    return temp1, hum1, temp2, hum2