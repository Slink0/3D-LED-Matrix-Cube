import matplotlib
matplotlib.use('TkAgg')
from display.cube import Cube
from visualize.VisualizeCube import VisualizeCube

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

# add def run_fluid later to test fluids


# Swap out the test pattern here to try different ones
ACTIVE_TEST = test_layer_sweep

def main():
    cube = Cube()
    visualizer = VisualizeCube(cube)

    def update(frame):
        ACTIVE_TEST(cube, frame)

    visualizer.run(update_fn=update)


if __name__ == '__main__':
    main()