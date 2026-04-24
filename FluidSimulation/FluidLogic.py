import numpy as np


class FluidSimulation:
    def __init__(self, size=8, fill_ratio=0.35):
        """
        Cellular automaton fluid simulation using numpy arrays.
        Each cell holds a float 0.0-1.0 representing fluid amount.
        Flow direction is driven by the gravity vector each step.

        :param size:       Cube dimension (8 for 8x8x8)
        :param fill_ratio: Fraction of cube height to fill with fluid
        """
        self.size = size
        self.fill_ratio = fill_ratio

        # Continuous value grid — float32 for speed
        self.grid = np.zeros((size, size, size), dtype=np.float32)
        self._initialize()

    # ─── Initialization ────────────────────────────────────────────────────────

    def _initialize(self):
        """Fill the bottom portion of the cube with fluid."""
        fill_height = int(self.size * self.fill_ratio)
        self.grid[:, :, :fill_height] = 1.0

    # ─── Simulation Step ───────────────────────────────────────────────────────

    def step(self, gravity):
        """
        Advance the simulation by one step.
        Processes each axis sequentially so fluid can propagate properly.

        :param gravity: List or array of [gx, gy, gz]
        """
        gx = float(gravity[0])
        gy = float(gravity[1])
        gz = float(gravity[2])

        mag = abs(gx) + abs(gy) + abs(gz) + 1e-6
        gx_n = gx / mag
        gy_n = gy / mag
        gz_n = gz / mag

        # Process each direction sequentially — strongest first
        directions = [
            ((1, 0, 0),  gx_n),  ((-1, 0, 0), -gx_n),
            ((0, 1, 0),  gy_n),  ((0, -1, 0), -gy_n),
            ((0, 0, 1),  gz_n),  ((0,  0, -1), -gz_n),
        ]
        directions.sort(key=lambda d: -d[1])

        for (dx, dy, dz), w in directions:
            if w <= 0.01:
                continue

            # Iterate sequentially in the flow direction so fluid cascades
            x_range = range(self.size) if dx >= 0 else range(self.size - 1, -1, -1)
            y_range = range(self.size) if dy >= 0 else range(self.size - 1, -1, -1)
            z_range = range(self.size) if dz >= 0 else range(self.size - 1, -1, -1)

            for x in x_range:
                for y in y_range:
                    for z in z_range:
                        amount = self.grid[x, y, z]
                        if amount < 0.01:
                            continue

                        nx, ny, nz = x + dx, y + dy, z + dz
                        if not (0 <= nx < self.size and 0 <= ny < self.size and 0 <= nz < self.size):
                            continue

                        space = 1.0 - self.grid[nx, ny, nz]
                        if space < 0.01:
                            continue

                        flow = min(amount * w * 0.8, space, amount)
                        self.grid[nx, ny, nz] += flow
                        self.grid[x, y, z] -= flow

        # Lateral spread using slices — fast numpy operation
        spread_dirs = [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0)]
        for dx, dy, dz in spread_dirs:
            sx = slice(max(0, -dx), self.size - max(0, dx))
            sy = slice(max(0, -dy), self.size - max(0, dy))
            sz = slice(max(0, -dz), self.size - max(0, dz))
            tx = slice(max(0, dx), self.size - max(0, -dx))
            ty = slice(max(0, dy), self.size - max(0, -dy))
            tz = slice(max(0, dz), self.size - max(0, -dz))

            space = np.maximum(0.0, 1.0 - self.grid[tx, ty, tz])
            spread = np.minimum(self.grid[sx, sy, sz] * 0.08, space)
            spread = np.maximum(spread, 0.0)

            self.grid[tx, ty, tz] += spread
            self.grid[sx, sy, sz] -= spread

        np.clip(self.grid, 0.0, 1.0, out=self.grid)

    # ─── Output ────────────────────────────────────────────────────────────────

    def get_voxels(self):
        """
        Convert the continuous grid to a binary 8x8x8 nested list for LED output.
        Cells above the threshold are considered lit.

        :return: 8x8x8 nested list of 0s and 1s
        """
        threshold = 0.25
        binary = (self.grid >= threshold).astype(np.uint8)

        # Convert numpy array to nested list for compatibility with renderer
        return binary.tolist()