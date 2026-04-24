import spidev
import RPi.GPIO as GPIO
import time

from hardware.FluidSimulation import GravityVector

from mpu6050 import MPU6050

mpu = MPU6050()
mpu.connect()
mpu.calibrate()

# Simple low-pass filter
prev_g = [0.0, 0.0, -1.0]

def get_smooth_gravity():
    global prev_g

    mpu.update()
    roll, pitch = mpu.get_angles()

    gravity.set_from_angles(roll, pitch)
    g = gravity.get()

    alpha = 0.2  # smoothing factor

    smoothed = [
        prev_g[0] * (1 - alpha) + g[0] * alpha,
        prev_g[1] * (1 - alpha) + g[1] * alpha,
        prev_g[2] * (1 - alpha) + g[2] * alpha,
    ]

    prev_g = smoothed
    return smoothed

class VoxelFluid:
    def __init__(self, size=8, fill_ratio=0.4):
        self.size = size
        
        # 3D grid of fluid
        self.grid = [[[0.0 for _ in range(size)] 
                            for _ in range(size)] 
                            for _ in range(size)]

        # Initialize fluid in bottom
        fill_height = int(size * fill_ratio)

        for x in range(size):
            for y in range(size):
                for z in range(fill_height):
                    self.grid[x][y][z] = 1.0

    # ─────────────────────────────
    # SIMULATION STEP
    # ─────────────────────────────
    def step(self, gravity):
        gx, gy, gz = gravity

        # Determine dominant gravity axis
        # Normalize gravity
        mag = abs(gx) + abs(gy) + abs(gz) + 1e-6
        gx_n = gx / mag
        gy_n = gy / mag
        gz_n = gz / mag

        # Move fluid proportionally
        for dx, dy, dz, weight in [
            (1,0,0,gx_n), (-1,0,0,-gx_n),
            (0,1,0,gy_n), (0,-1,0,-gy_n),
            (0,0,1,gz_n), (0,0,-1,-gz_n),
        ]:
            if weight <= 0:
                continue

            nx, ny, nz = x+dx, y+dy, z+dz

            if 0 <= nx < self.size and 0 <= ny < self.size and 0 <= nz < self.size:
                flow = amount * weight * 0.5
                new_grid[nx][ny][nz] += flow
                new_grid[x][y][z] -= flow

        # Create new grid
        new_grid = [[[0.0 for _ in range(self.size)] 
                            for _ in range(self.size)] 
                            for _ in range(self.size)]

        for x in range(self.size):
            for y in range(self.size):
                for z in range(self.size):

                    amount = self.grid[x][y][z]
                    if amount < 0.01:
                        continue

                    # Try to move in gravity direction
                    nx, ny, nz = x, y, z

                    if axis == 0:
                        nx += direction
                    elif axis == 1:
                        ny += direction
                    else:
                        nz += direction

                    # Check bounds
                    if 0 <= nx < self.size and 0 <= ny < self.size and 0 <= nz < self.size:
                        flow = min(amount, 0.5)

                        new_grid[nx][ny][nz] += flow
                        new_grid[x][y][z] += amount - flow
                    else:
                        new_grid[x][y][z] += amount

                    # Sideways spread (makes it look fluid)
                    for dx, dy, dz in [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0)]:
                        sx, sy, sz = x+dx, y+dy, z+dz
                        if 0 <= sx < self.size and 0 <= sy < self.size and 0 <= sz < self.size:
                            spread = amount * 0.02
                            new_grid[sx][sy][sz] += spread
                            new_grid[x][y][z] -= spread

        self.grid = new_grid

    # ─────────────────────────────
    # OUTPUT TO LED CUBE
    # ─────────────────────────────
    def get_voxels(self):
        cube = [[[0]*self.size for _ in range(self.size)] for _ in range(self.size)]

        for x in range(self.size):
            for y in range(self.size):
                for z in range(self.size):
                    if self.grid[x][y][z] > 0.2:  # threshold
                        cube[x][y][z] = 1

        return cube
# CONFIG
LATCH = 25
LAYER_PINS = [5, 6, 12, 13, 16, 19, 20, 21]
NUM_REGS = 8

# SETUP
GPIO.setmode(GPIO.BCM)
GPIO.setup(LATCH, GPIO.OUT)

for pin in LAYER_PINS:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, 0)

spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 8000000  # more stable than 13MHz

# SIM
sim = VoxelFluid()
gravity = GravityVector()

# ─────────────────────────────────────────────
# FAST VOXEL BUFFER (no numpy)
# ─────────────────────────────────────────────
def build_cube(sim, gravity):
    g = get_smooth_gravity()
    sim.step(g)
    return sim.get_voxels()

# ─────────────────────────────────────────────
# MUCH FASTER BYTE PACKING
# ─────────────────────────────────────────────
def cube_to_bytes(cube, z):
    data = [0]*8

    for y in range(8):
        byte = 0
        for x in range(8):
            if cube[x][y][z]:
                byte |= (1 << x)
        data[7 - y] = byte  # reverse for shift order

    return data

# ─────────────────────────────────────────────
# LOW LEVEL OUTPUT
# ─────────────────────────────────────────────
def write_columns(data):
    GPIO.output(LATCH, 0)
    spi.xfer(data)
    GPIO.output(LATCH, 1)

def all_layers_off():
    for pin in LAYER_PINS:
        GPIO.output(pin, 0)

# ─────────────────────────────────────────────
# MAIN LOOP
# ─────────────────────────────────────────────
try:
    while True:

        g = get_smooth_gravity()

        sim.step(g)
        cube = sim.get_voxels()

        for _ in range(20):
            for z in range(8):

                all_layers_off()

                data = cube_to_bytes(cube, z)
                write_columns(data)

                GPIO.output(LAYER_PINS[z], 1)

                time.sleep(0.001)

except KeyboardInterrupt:
    pass

finally:
    write_columns([0]*NUM_REGS)
    all_layers_off()
    spi.close()
    GPIO.cleanup()
