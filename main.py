import matplotlib
matplotlib.use('TkAgg')
from display.cube import Cube
from visualize.VisualizeCube import VisualizeCube
from config import USE_VIRTUAL_GYRO

def test_layer_sweep(cube, frame):
    """Sweeps a full layer of LEDs along the Z axis one at a time."""
    cube.clear()
    layer = frame % cube.size
    for x in range(cube.size):
        for y in range(cube.size):
            cube.set_led(x, y, layer, True)


def test_fill_and_clear(cube, frame):
    """Alternates between fully filled and fully cleared every 20 frames."""
    if (frame // 20) % 2 == 0:
        cube.fill()
    else:
        cube.clear()


def test_diagonal(cube, frame):
    """Moves a diagonal line of LEDs across the cube."""
    cube.clear()
    offset = frame % cube.size
    for i in range(cube.size):
        x = (i + offset) % cube.size
        cube.set_led(x, i, i, True)


def test_random(cube, frame):
    """Randomly turns LEDs on and off to stress test the grid and renderer."""
    import random
    cube.clear()
    for _ in range(64):
        x = random.randint(0, cube.size - 1)
        y = random.randint(0, cube.size - 1)
        z = random.randint(0, cube.size - 1)
        cube.set_led(x, y, z, True)


def test_single_led(cube, frame):
    """Steps a single LED through every position in the cube sequentially."""
    cube.clear()
    total = cube.size ** 3
    idx = frame % total
    x = idx // (cube.size * cube.size)
    y = (idx // cube.size) % cube.size
    z = idx % cube.size
    cube.set_led(x, y, z, True)

def run_fluid(cube, sim, gravity):
    """
    Steps the fluid simulation and writes the resulting voxels to the cube grid.

    :param cube:    Cube instance
    :param sim:     FluidSimulation instance
    :param gravity: GravityVector instance
    """
    sim.step(gravity.get())
    cube.clear()
    for (x, y, z) in sim.get_voxels():
        cube.set_led(x, y, z, True)

# Set to True to run the fluid simulation, False to run a test pattern
RUN_FLUID = True

# Swap out the test pattern here to try different ones
ACTIVE_TEST = test_single_led


def main():
    from FluidSimulation.FluidLogic import FluidSimulation
    from FluidSimulation.gravity import GravityVector

    cube = Cube()
    visualizer = VisualizeCube(cube)

    if RUN_FLUID:
        sim = FluidSimulation()
        gravity = GravityVector()

        # Set up the MPU6050 if we are not using the virtual gyro
        mpu = None
        if not USE_VIRTUAL_GYRO:
            try:
                from hardware.mpu6050 import MPU6050
                mpu = MPU6050()
                mpu.connect()
                mpu.calibrate()
            except Exception as e:
                print(f"[main] MPU6050 unavailable: {e}")
                print("[main] Falling back to fixed gravity vector.")
                mpu = None

        def update(frame):
            if USE_VIRTUAL_GYRO:
                # Read view angles from the visualizer and pass to gravity
                elev, azim = visualizer.get_view_angles()
                gravity.set_from_visualizer(elev, azim)
            elif mpu is not None:
                # Read angles from the physical MPU6050 and pass to gravity
                mpu.update()
                roll, pitch = mpu.get_angles()
                gravity.set_from_angles(roll, pitch)
            # If neither is available, gravity stays as fixed downward default

            run_fluid(cube, sim, gravity)

    else:
        def update(frame):
            ACTIVE_TEST(cube, frame)

    visualizer.run(update_fn=update)


if __name__ == '__main__':
    main()