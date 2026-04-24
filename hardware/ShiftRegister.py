import time

try:
    import spidev
    import RPi.GPIO as GPIO
    HARDWARE_AVAILABLE = True
except ImportError:
    HARDWARE_AVAILABLE = False
    print("[ShiftRegister] RPi.GPIO or spidev not found — hardware unavailable.")

from config import LATCH_PIN, LAYER_PINS, NUM_REGISTERS, SPI_SPEED


class ShiftRegister:
    def __init__(self):
        """
        Controls the SN74HC595 shift registers via SPI.
        Uses a latch pin to control when data is committed to the outputs.
        8 shift registers are chained together for 64 column outputs.
        """
        if not HARDWARE_AVAILABLE:
            return

        self.latch = LATCH_PIN
        self.layer_pins = LAYER_PINS
        self.num_registers = NUM_REGISTERS

        GPIO.setmode(GPIO.BCM)

        # Setup latch pin
        GPIO.setup(self.latch, GPIO.OUT)

        # Setup layer MOSFET pins — all off by default
        for pin in self.layer_pins:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, 0)

        # Setup SPI
        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)
        self.spi.max_speed_hz = SPI_SPEED

    def write_columns(self, data: list):
        """
        Shift a list of bytes out to the shift registers via SPI.
        Pulses the latch pin to commit the data to the outputs.

        :param data: List of 8 bytes representing 64 column states
        """
        GPIO.output(self.latch, 0)
        self.spi.xfer(data)
        GPIO.output(self.latch, 1)

    def set_layer(self, layer: int, prev: int):
        """
        Switch the active layer by turning off the previous MOSFET
        and turning on the new one.

        :param layer: Index of the layer to turn on (0-7)
        :param prev:  Index of the previously active layer to turn off
        """
        GPIO.output(self.layer_pins[prev], 0)
        GPIO.output(self.layer_pins[layer], 1)

    def all_layers_off(self):
        """Turn off all layer MOSFETs."""
        for pin in self.layer_pins:
            GPIO.output(pin, 0)

    def clear(self):
        """Turn off all LEDs — zero out shift registers and all layers."""
        self.write_columns([0] * self.num_registers)
        self.all_layers_off()

    def cube_to_bytes(self, cube, z: int) -> list:
        """
        Convert a single layer of the cube grid into 8 bytes for the shift registers.
        Maps x, y coordinates to a 64-bit value where each bit represents one LED.

        :param cube: 8x8x8 numpy array of LED states
        :param z:    Layer index (0-7)
        :return:     List of 8 bytes ready to send via SPI
        """
        layer_data = 0

        for x in range(8):
            for y in range(8):
                if cube[x][y][z]:
                    index = y * 8 + x
                    layer_data |= (1 << index)

        bytes_out = []
        for i in range(8):
            bytes_out.append((layer_data >> 8 * i) & 0xFF)

        bytes_out.reverse()
        return bytes_out

    def cleanup(self):
        """Release SPI and GPIO resources cleanly on shutdown."""
        if not HARDWARE_AVAILABLE:
            return
        self.clear()
        self.spi.close()
        GPIO.cleanup()