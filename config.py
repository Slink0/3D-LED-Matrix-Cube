# 8x8x8
CUBE_SIZE = 8

#SN74HC595
DATA_PIN = None
CLOCK_PIN = None
LATCH_PIN = None

MPU6050_ADDRESS = 0x68

GRAVITY = 9.8
SIMULATION_SPEED = 0.20

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

# Set True to use visualizer rotation as gyro input false for pi
USE_VIRTUAL_GYRO = False

# Testing MPU without the cube
USE_MPU_STREAM   = True
MPU_STREAM_PORT = 5005