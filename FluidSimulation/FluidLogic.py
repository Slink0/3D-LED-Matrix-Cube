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
        Advance the simulation by one step using numpy slice operations.
        Each axis-aligned direction is processed in order of gravity strength.
        Fluid flows into neighboring cells proportional to gravity weight
        and available space.

        :param gravity: List or array of [gx, gy, gz]
        """
        gx = float(gravity[0])
        gy = float(gravity[1])
        gz = float(gravity[2])

        mag = abs(gx) + abs(gy) + abs(gz) + 1e-6
        gx_n = gx / mag
        gy_n = gy / mag
        gz_n = gz / mag

        # Build direction list sorted by strongest gravity pull first
        directions = [
            ((1, 0, 0),  gx_n),  ((-1, 0, 0), -gx_n),
            ((0, 1, 0),  gy_n),  ((0, -1, 0), -gy_n),
            ((0, 0, 1),  gz_n),  ((0,  0, -1), -gz_n),
        ]
        directions.sort(key=lambda d: -d[1])

        new_grid = self.grid.copy()

        for (dx, dy, dz), w in directions:
            if w <= 0.01:
                continue

            # Source slice — cells that have fluid to give
            sx = slice(max(0, -dx), self.size - max(0, dx))
            sy = slice(max(0, -dy), self.size - max(0, dy))
            sz = slice(max(0, -dz), self.size - max(0, dz))

            # Target slice — cells that receive fluid
            tx = slice(max(0, dx), self.size - max(0, -dx))
            ty = slice(max(0, dy), self.size - max(0, -dy))
            tz = slice(max(0, dz), self.size - max(0, -dz))

            src = new_grid[sx, sy, sz]
            tgt = new_grid[tx, ty, tz]

            # Flow is limited by available space in target and amount in source
            space = np.maximum(0.0, 1.0 - tgt)
            flow = np.minimum(src * w * 0.9, space)
            flow = np.maximum(flow, 0.0)

            new_grid[tx, ty, tz] += flow
            new_grid[sx, sy, sz] -= flow

        # Lateral spread — fluid fills gaps sideways
        spread_dirs = [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0)]
        for dx, dy, dz in spread_dirs:
            sx = slice(max(0, -dx), self.size - max(0, dx))
            sy = slice(max(0, -dy), self.size - max(0, dy))
            sz = slice(max(0, -dz), self.size - max(0, dz))
            tx = slice(max(0, dx), self.size - max(0, -dx))
            ty = slice(max(0, dy), self.size - max(0, -dy))
            tz = slice(max(0, dz), self.size - max(0, -dz))

            src = new_grid[sx, sy, sz]
            tgt = new_grid[tx, ty, tz]

            space = np.maximum(0.0, 1.0 - tgt)
            spread = np.minimum(src * 0.1, space)
            spread = np.maximum(spread, 0.0)

            new_grid[tx, ty, tz] += spread
            new_grid[sx, sy, sz] -= spread

        self.grid = np.clip(new_grid, 0.0, 1.0)

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