import random


class FluidSimulation:
    def __init__(self, size=8, fill_ratio=0.375):
        """
        Cellular automaton fluid simulation using a continuous value grid.
        Each cell holds a float 0.0-1.0 representing fluid amount.
        Flow direction is driven by the gravity vector each step.

        :param size:       Cube dimension (8 for 8x8x8)
        :param fill_ratio: Fraction of cube volume to fill with fluid
        """
        self.size = size
        self.fill_ratio = fill_ratio

        # Continuous value grid — each cell is 0.0 (empty) to 1.0 (full)
        self.grid = [[[0.0 for _ in range(size)]
                           for _ in range(size)]
                           for _ in range(size)]

        self._initialize()

    # ─── Initialization ────────────────────────────────────────────────────────

    def _initialize(self):
        """Fill the bottom portion of the cube with fluid."""
        fill_height = int(self.size * self.fill_ratio)
        for x in range(self.size):
            for y in range(self.size):
                for z in range(fill_height):
                    self.grid[x][y][z] = 1.0

    # ─── Helpers ───────────────────────────────────────────────────────────────

    def _in_bounds(self, x, y, z) -> bool:
        return 0 <= x < self.size and 0 <= y < self.size and 0 <= z < self.size

    def _clamp(self, val, lo=0.0, hi=1.0) -> float:
        return max(lo, min(hi, val))

    # ─── Simulation Step ───────────────────────────────────────────────────────

    def step(self, gravity):
        """
        Advance the simulation by one step using the gravity vector.

        Flow rules:
        1. Each cell with fluid tries to move in the gravity direction,
           proportional to how strongly gravity pulls that way.
        2. If the target cell is already full, fluid spreads sideways
           along the plane perpendicular to gravity.
        3. A small random lateral spread is applied each frame to
           simulate surface tension breaking down and fluid finding gaps.

        :param gravity: List or array of [gx, gy, gz]
        """
        gx, gy, gz = gravity[0], gravity[1], gravity[2]

        # Normalize gravity to get flow weights per axis
        mag = abs(gx) + abs(gy) + abs(gz) + 1e-6
        gx_n = gx / mag
        gy_n = gy / mag
        gz_n = gz / mag

        # Build list of (dx, dy, dz, weight) for each gravity direction
        # Only directions with positive weight (i.e. gravity pulls that way)
        directions = []
        for dx, dy, dz, w in [
            (1, 0, 0,  gx_n), (-1, 0, 0, -gx_n),
            (0, 1, 0,  gy_n), (0, -1, 0, -gy_n),
            (0, 0, 1,  gz_n), (0,  0, -1, -gz_n),
        ]:
            if w > 0.01:
                directions.append((dx, dy, dz, w))

        # Sort by strongest gravity pull first
        directions.sort(key=lambda d: d[3], reverse=True)

        # Sideways spread directions
        spread_dirs = [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]

        # New grid starts as a copy of current
        new_grid = [[[self.grid[x][y][z]
                      for z in range(self.size)]
                      for y in range(self.size)]
                      for x in range(self.size)]

        for x in range(self.size):
            for y in range(self.size):
                for z in range(self.size):
                    amount = self.grid[x][y][z]
                    if amount < 0.01:
                        continue

                    # Try to flow in each gravity direction
                    for dx, dy, dz, weight in directions:
                        nx, ny, nz = x + dx, y + dy, z + dz

                        if not self._in_bounds(nx, ny, nz):
                            continue

                        space = 1.0 - new_grid[nx][ny][nz]
                        if space < 0.01:
                            continue

                        flow = self._clamp(amount * weight * 0.9, 0.0, min(amount, space))

                        new_grid[nx][ny][nz] += flow
                        new_grid[x][y][z]    -= flow
                        amount               -= flow

                        if amount < 0.01:
                            break

                    # Sideways spread
                    if amount > 0.05:
                        random.shuffle(spread_dirs)
                        for dx, dy, dz in spread_dirs:
                            nx, ny, nz = x + dx, y + dy, z + dz

                            if not self._in_bounds(nx, ny, nz):
                                continue

                            space = 1.0 - new_grid[nx][ny][nz]
                            if space < 0.01:
                                continue

                            spread = self._clamp(amount * 0.15, 0.0, min(amount, space))
                            new_grid[nx][ny][nz] += spread
                            new_grid[x][y][z]    -= spread
                            amount               -= spread

                            if amount < 0.01:
                                break

        # Clamp and commit
        for x in range(self.size):
            for y in range(self.size):
                for z in range(self.size):
                    self.grid[x][y][z] = self._clamp(new_grid[x][y][z])

    # ─── Output ────────────────────────────────────────────────────────────────

    def get_voxels(self):
        """
        Convert the continuous grid to a binary 8x8x8 nested list for LED output.
        Cells above the threshold are considered lit.

        :return: 8x8x8 nested list of 0s and 1s
        """
        threshold = 0.25
        cube = [[[0] * self.size for _ in range(self.size)] for _ in range(self.size)]

        for x in range(self.size):
            for y in range(self.size):
                for z in range(self.size):
                    if self.grid[x][y][z] >= threshold:
                        cube[x][y][z] = 1

        return cube