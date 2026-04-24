import spidev
import RPi.GPIO as GPIO
import time

LATCH = 25
LAYER_PINS = [5, 6, 12, 13, 16, 19, 20, 21]

GPIO.setmode(GPIO.BCM)
GPIO.setup(LATCH, GPIO.OUT)
for pin in LAYER_PINS:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, 0)

spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 8000000

# Turn on all LEDs in layer 0
GPIO.output(LATCH, 0)
spi.xfer([0xFF]*8)
GPIO.output(LATCH, 1)
GPIO.output(LAYER_PINS[0], 1)

print('Layer 0 should be fully lit')
time.sleep(5)

GPIO.output(LAYER_PINS[0], 0)
spi.xfer([0]*8)
GPIO.cleanup()
print('Done')