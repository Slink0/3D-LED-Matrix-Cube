import spidev
import RPi.GPIO as GPIO
import time
import numpy as np
from hardware.FluidSimulation import FluidSimulation
from hardware.FluidSimulation import GravityVector


# CONFIG
LATCH = 25
LAYER_PINS = [5, 6, 12, 13, 16, 19, 20, 21]
NUM_REGS = 8  # 8 shift registers = 64 columns

# SETUP
GPIO.setmode(GPIO.BCM)

# Setup latch
GPIO.setup(LATCH, GPIO.OUT)

# Setup layer MOSFET pins
for pin in LAYER_PINS:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, 0)  # all layers OFF

# Setup SPI
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 13000000


# FUNCTIONS
def write_columns(data):
    GPIO.output(LATCH, 0)
    spi.xfer(data)
    GPIO.output(LATCH, 1)

def all_layers_off():
    for pin in LAYER_PINS:
        GPIO.output(pin, 0)

def set_layer(layer, prev=0):
    GPIO.output(LAYER_PINS[prev], 0)
    GPIO.output(LAYER_PINS[layer], 1)

def normalize(val, min_val, max_val):
    return int((val - min_val) / (max_val - min_val) * 7)

def wave(t=0):
    cube = np.zeros((8,8,8), dtype=int)
    for x in range(8):
        for y in range(8):
            xr = (x / 7) * 2 * np.pi
            yr = (y / 7) * 2 * np.pi
            
            z_real = np.sin((xr + t)*0.5) * np.cos((yr + t)*0.5)

            z = int((z_real + 1) / 2 * 7)

            cube[x][y][z] = 1

x_vals = (np.arange(8) / 7) * 2 * np.pi
y_vals = (np.arange(8) / 7) * 2 * np.pi 

def wave_fast(t):
    cube = np.zeros((8,8,8), dtype=np.uint8)

    for x in range(8):
        for y in range(8):
            
            z_real = (np.sin((x_vals[x] + t)*0.5) * np.cos((y_vals[y] + t)*0.5)) * 1.2
            z = int((z_real+1) * 3.5)  

            cube[x][y][z] = 1

    return cube


sim = FluidSimulation()
gravity = GravityVector()

def run_fluid(sim, gravity):
    """
    Steps the fluid simulation and writes the resulting voxels to the cube grid.

    :param cube:    Cube instance
    :param sim:     FluidSimulation instance
    :param gravity: GravityVector instance
    """
    cube = np.zeros((8,8,8), dtype=np.uint8)
    sim.step(gravity.get())
    for (x, y, z) in sim.get_voxels():
        if 0 <= x < 8 and 0 <= y < 8 and 0 <= z < 8:
            # print(f"x: {x}, y: {y}: z: {z}")
            cube[x][y][z] = 1

    return cube

def cube_tobytes(cube, z):
    layer_data = 0
    bytes_out = []

    for x in range(8):
        for y in range(8):
            if cube[x][y][z]:
                index = y * 8 + x
                layer_data |= (1<<index)
    
    for i in range(8):
        bytes_out.append((layer_data >> 8 * i) & 0xFF)

    bytes_out.reverse()

    return bytes_out


# MAIN TEST LOOP
t = 0
prev_row = 0
try:
    
    while True:
          # layer
        cube = wave_fast(t)
        t += 0.01

        for z in range(8):
            data = cube_tobytes(cube, z)

            GPIO.output(LAYER_PINS[prev_row], 0)
            write_columns(data)
            GPIO.output(LAYER_PINS[z], 1)
            
            prev_row = z
            time.sleep(0.00005)

                


except KeyboardInterrupt:
    pass

finally:
    write_columns([0]*NUM_REGS)
    all_layers_off()
    spi.close()
    GPIO.cleanup()
