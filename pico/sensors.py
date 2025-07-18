import board
import busio
import adafruit_ahtx0
import digitalio

def set_up_sensors():
    # I2C0 on GPIO 0 (SDA), GPIO 1 (SCL)
    i2c0 = busio.I2C(board.GP1, board.GP0)
    sensor1 = adafruit_ahtx0.AHTx0(i2c0)
    # I2C1 on GPIO 2 (SDA), GPIO 3 (SCL)
    i2c1 = busio.I2C(board.GP3, board.GP2)
    sensor2 = adafruit_ahtx0.AHTx0(i2c1)
    return sensor1, sensor2

def read_sensors(sensor1, sensor2):
    temp1 = sensor1.temperature
    hum1 = sensor1.relative_humidity
    temp2 = sensor2.temperature
    hum2 = sensor2.relative_humidity
    return temp1, hum1, temp2, hum2

def set_up_switch():
    sw = digitalio.DigitalInOut(board.GP15)
    sw.direction = digitalio.Direction.INPUT
    sw.pull = digitalio.Pull.UP
    return sw