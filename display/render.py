import time
import numpy as np

try:
    import RPi.GPIO as GPIO

    HARDWARE_AVAILABLE = True
except ImportError:
    HARDWARE_AVAILABLE = False

from hardware.ShiftRegister import ShiftRegister
from config import LAYER_DELAY


class Renderer:
    def __init__(self):
        """
        Drives the physical LED cube by multiplexing through each layer.
        Uses ShiftRegister to send column data and switch layers.
        """
        self.sr = ShiftRegister()
        self._prev_layer = 0

    # ─── Core Render ───────────────────────────────────────────────────────────

    def render(self, cube):
        """
        Multiplex through all 8 layers of the cube, displaying each one
        briefly. Call this in a tight loop to produce a solid looking display.

        :param cube: 8x8x8 numpy array of LED states (1 = on, 0 = off)
        """
        for z in range(8):
            data = self.sr.cube_to_bytes(cube, z)
            self.sr.set_layer(z, self._prev_layer)
            self.sr.write_columns(data)
            self._prev_layer = z
            time.sleep(LAYER_DELAY)
    def render_voxels(self, cube):
        """
        Multiplex through all 8 layers using a voxel list (nested lists).
        Uses faster byte packing based on Nic's implementation.
        :param cube: 8x8x8 nested list of LED states (1 = on, 0 = off)
        """
        for z in range(8):
            data = self._voxels_to_bytes(cube, z)
            self.sr.all_layers_off()
            self.sr.write_columns(data)
            GPIO.output(self.sr.layer_pins[z], 1)
            time.sleep(LAYER_DELAY)

    @staticmethod
    def _voxels_to_bytes(cube, z) -> list:
        """
        Faster byte packing for nested list voxel format.
        Packs each row of 8 x-values into a single byte.

        :param cube: 8x8x8 nested list
        :param z:    Layer index
        :return:     List of 8 bytes
        """
        data = [0] * 8
        for y in range(8):
            byte = 0
            for x in range(8):
                if cube[x][y][z]:
                    byte |= (1 << x)
            data[7 - y] = byte
        return data
    def clear(self):
        """Turn off all LEDs."""
        self.sr.clear()

    def cleanup(self):
        """Release all hardware resources."""
        self.sr.cleanup()

    # ─── Test Patterns ─────────────────────────────────────────────────────────

    def test_layer_sweep(self, cycles: int = 3):
        """
        Light up one full layer at a time, sweeping from bottom to top.

        :param cycles: Number of full sweeps to perform
        """
        for _ in range(cycles):
            for z in range(8):
                cube = np.zeros((8, 8, 8), dtype=np.uint8)
                cube[:, :, z] = 1
                for _ in range(50):  # Hold each layer for 50 render passes
                    self.render(cube)

    def test_fill_and_clear(self, cycles: int = 3):
        """
        Alternate between fully lit and fully dark.

        :param cycles: Number of on/off cycles
        """
        for _ in range(cycles):
            cube = np.ones((8, 8, 8), dtype=np.uint8)
            for _ in range(100):
                self.render(cube)
            cube = np.zeros((8, 8, 8), dtype=np.uint8)
            for _ in range(100):
                self.render(cube)

    def test_single_led(self):
        """Step a single LED through every position in the cube sequentially."""
        for x in range(8):
            for y in range(8):
                for z in range(8):
                    cube = np.zeros((8, 8, 8), dtype=np.uint8)
                    cube[x][y][z] = 1
                    for _ in range(20):
                        self.render(cube)

    def test_wave(self, duration: float = 10.0):
        """
        Display a sine wave animation across the cube surface.

        :param duration: How long to run the wave in seconds
        """
        x_vals = (np.arange(8) / 7) * 2 * np.pi
        y_vals = (np.arange(8) / 7) * 2 * np.pi
        t = 0
        start = time.time()

        while time.time() - start < duration:
            cube = np.zeros((8, 8, 8), dtype=np.uint8)
            for x in range(8):
                for y in range(8):
                    z_real = (np.sin((x_vals[x] + t) * 0.5) * np.cos((y_vals[y] + t) * 0.5)) * 1.2
                    z = int((z_real + 1) * 3.5)
                    z = np.clip(z, 0, 7)
                    cube[x][y][z] = 1
            t += 0.01
            self.render(cube)