import board
import busio

uart = busio.UART(tx=board.GP16, rx=board.GP17, baudrate=115200)

def log(message):
    print(message)
    uart.write(message.encode('utf-8') + b'\r\n')