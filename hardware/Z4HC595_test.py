import spidev
import RPi.GPIO as GPIO
import time

LATCH = 25       # RCLK pin
NUM_REGS = 8     # CHANGE THIS (e.g., 8 for full cube)

GPIO.setmode(GPIO.BCM)
GPIO.setup(LATCH, GPIO.OUT)

spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1000000

def write_registers(data):
    GPIO.output(LATCH, 0)
    spi.xfer(data)
    GPIO.output(LATCH, 1)

try:
    while True:
        total_bits = NUM_REGS * 8

        for i in range(total_bits):
            data = [0] * NUM_REGS

            reg_index = i // 8
            bit_index = i % 8

            data[NUM_REGS - 1 - reg_index] = 1 << bit_index

            write_registers(data)
            time.sleep(0.1)

except KeyboardInterrupt:
    pass

finally:
    write_registers([0] * NUM_REGS)
    spi.close()
    GPIO.cleanup()