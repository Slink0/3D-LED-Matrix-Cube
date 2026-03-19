import numpy as np
from config import CUBE_SIZE


class Cube:
    def __init__(self):
        """Initialize the 8x8x8 grid with all LEDs off."""
        self.size = CUBE_SIZE
        self.grid = np.zeros((self.size, self.size, self.size), dtype=bool)

    def set_led(self, x, y, z, state: bool):
        """Turn a single LED on or off."""
        if self._in_bounds(x, y, z):
            self.grid[x][y][z] = state

    def get_led(self, x, y, z) -> bool:
        """Return the state of a single LED."""
        if self._in_bounds(x, y, z):
            return self.grid[x][y][z]
        return False

    def clear(self):
        """Turn all LEDs off."""
        self.grid[:] = False

    def fill(self):
        """Turn all LEDs on."""
        self.grid[:] = True

    def get_grid(self):
        """Return the full grid state."""
        return self.grid

    def _in_bounds(self, x, y, z) -> bool:
        """Check that coordinates are within the cube."""
        return 0 <= x < self.size and 0 <= y < self.size and 0 <= z < self.size