import spidev
import RPi.GPIO as GPIO
import time

LATCH = 25  # GPIO pin for RCLK (latch)

GPIO.setmode(GPIO.BCM)
GPIO.setup(LATCH, GPIO.OUT)

# Setup SPI
spi = spidev.SpiDev()
spi.open(0, 0)  # bus 0, CE0
spi.max_speed_hz = 1000000

def write_byte(value):
    GPIO.output(LATCH, 0)   # latch LOW
    spi.xfer([value])       # send 8 bits
    GPIO.output(LATCH, 1)   # latch HIGH

try:
    while True:
        for i in range(8):
            value = 1 << i   # shift single HIGH bit
            write_byte(value)
            time.sleep(0.2)

except KeyboardInterrupt:
    pass

finally:
    write_byte(0x00)  # turn everything off
    spi.close()
    GPIO.cleanup()