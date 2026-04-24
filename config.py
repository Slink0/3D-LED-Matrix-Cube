# 8x8x8
CUBE_SIZE = 8

#SN74HC595
SPI_SPEED   = 13000000
NUM_REGISTERS = 8
LAYER_PINS = [5, 6, 12, 13, 16, 19, 20, 21]
LATCH_PIN = 25
LAYER_DELAY = 0.00005

MPU6050_ADDRESS = 0x68

# Dark grey when off and blue when on
LED_OFF_COLOR = (0.15, 0.15, 0.15)
LED_ON_COLOR = (0.1, 0.4, 1.0)
LED_SIZE = 100

# Sim
GRAVITY = 9.8
SIMULATION_SPEED = 0.15
FLUID_FILL_RATIO = 0.75
PARTICLE_MASS = 1.0
# damping on wall collision (0 = no bounce, 1 = full bounce)
DAMPING = 0.4
# Velocity retention per frame (lower = thicker fluid)
VISCOSITY = 0.87
PARTICLE_RADIUS = 0.5
COLLISION_DAMPING = 0.8
# size for spatial hashing grid
SPATIAL_HASH_CELL_SIZE = 1.0

RUN_ON_PI = True
RUN_FLUID = True

# Set True to use visualizer rotation as gyro input false for pi
USE_VIRTUAL_GYRO = False

# Testing MPU without the cube
USE_MPU_STREAM   = False
MPU_STREAM_PORT = 5005