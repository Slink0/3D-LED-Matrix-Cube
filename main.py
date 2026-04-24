from config import USE_VIRTUAL_GYRO, USE_MPU_STREAM, RUN_ON_PI

# ─── Test Patterns ─────────────────────────────────────────────────────────────

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


# ─── Fluid Simulation ──────────────────────────────────────────────────────────

def run_fluid_visualizer(cube, sim, gravity):
    """
    Steps the fluid simulation and updates the Cube instance for the visualizer.
    """
    sim.step(gravity.get())
    cube.clear()
    voxels = sim.get_voxels()
    for x in range(8):
        for y in range(8):
            for z in range(8):
                if voxels[x][y][z]:
                    cube.set_led(x, y, z, True)


def run_fluid_pi(sim, gravity):
    """
    Steps the fluid simulation and returns a numpy grid for the renderer.
    """
    import numpy as np
    sim.step(gravity.get())
    grid = np.zeros((8, 8, 8), dtype=np.uint8)
    for (x, y, z) in sim.get_voxels():
        if 0 <= x < 8 and 0 <= y < 8 and 0 <= z < 8:
            grid[x][y][z] = 1
    return grid


# ─── Gravity Source Setup ──────────────────────────────────────────────────────

def setup_gravity(visualizer=None):
    """
    Set up the gravity source based on config flags.
    Returns (gravity, mpu, mpu_receive).
    """
    from FluidSimulation.gravity import GravityVector
    gravity = GravityVector()
    mpu = None
    mpu_receive = None

    if USE_MPU_STREAM:
        try:
            from tempStream.mpu_receive import start, get_angles
            start()
            mpu_receive = get_angles
            print("[main] Receiving MPU6050 stream from Pi.")
        except Exception as e:
            print(f"[main] Could not start MPU stream receiver: {e}")

    elif not USE_VIRTUAL_GYRO:
        try:
            from hardware.mpu6050 import MPU6050
            mpu = MPU6050()
            mpu.connect()
            mpu.calibrate()
        except Exception as e:
            print(f"[main] MPU6050 unavailable: {e}")
            print("[main] Falling back to fixed gravity vector.")

    return gravity, mpu, mpu_receive


def update_gravity(gravity, mpu, mpu_receive, visualizer=None):
    """Update the gravity vector from whatever source is currently active."""
    if USE_VIRTUAL_GYRO and visualizer is not None:
        elev, azim = visualizer.get_view_angles()
        gravity.set_from_visualizer(elev, azim)
    elif USE_MPU_STREAM and mpu_receive is not None:
        roll, pitch = mpu_receive()
        gravity.set_from_angles(roll, pitch)
    elif mpu is not None:
        mpu.update()
        roll, pitch = mpu.get_angles()
        gravity.set_from_angles(roll, pitch)
    # else: gravity stays as fixed downward default


# ─── Main ──────────────────────────────────────────────────────────────────────

# Set to True to run the fluid simulation, False to run a test pattern
RUN_FLUID = False

# Swap out the test pattern here to try different ones
ACTIVE_TEST = test_layer_sweep


def main():
    from FluidSimulation.FluidLogic import FluidSimulation

    if RUN_ON_PI:
        # ── Physical cube on Raspberry Pi ──────────────────────────────────────
        from display.render import Renderer
        renderer = Renderer()

        if not RUN_FLUID:
            renderer.test_wave()
            renderer.cleanup()
            return

        sim = FluidSimulation()
        gravity, mpu, mpu_receive = setup_gravity()

        # Low pass filter state for smooth gravity
        prev_g = [0.0, 0.0, -9.8]
        alpha = 0.2  # smoothing factor — lower = smoother but slower to respond

        def get_smooth_gravity():
            update_gravity(gravity, mpu, mpu_receive)
            g = gravity.get()
            prev_g[0] = prev_g[0] * (1 - alpha) + g[0] * alpha
            prev_g[1] = prev_g[1] * (1 - alpha) + g[1] * alpha
            prev_g[2] = prev_g[2] * (1 - alpha) + g[2] * alpha
            return prev_g[:]

        try:
            while True:
                # Get smoothed gravity and step simulation once
                g = get_smooth_gravity()
                sim.step(g)
                cube = sim.get_voxels()

                # Render the same frame 20 times to keep display solid
                # while simulation computes next frame
                for _ in range(20):
                    renderer.render_voxels(cube)

        except KeyboardInterrupt:
            print("\n[main] Shutting down.")
        finally:
            renderer.cleanup()

    else:
        # ── Visualizer mode on PC ──────────────────────────────────────────────
        import matplotlib
        matplotlib.use('TkAgg')
        from display.cube import Cube
        from visualize.VisualizeCube import VisualizeCube

        cube = Cube()
        visualizer = VisualizeCube(cube)

        if RUN_FLUID:
            sim = FluidSimulation()
            gravity, mpu, mpu_receive = setup_gravity(visualizer)

            def update(frame):
                update_gravity(gravity, mpu, mpu_receive, visualizer)
                run_fluid_visualizer(cube, sim, gravity)
        else:
            def update(frame):
                ACTIVE_TEST(cube, frame)

        visualizer.run(update_fn=update)


if __name__ == '__main__':
    main()