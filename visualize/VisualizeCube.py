import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from config import CUBE_SIZE, LED_OFF_COLOR, LED_ON_COLOR, LED_SIZE, SIMULATION_SPEED


class VisualizeCube:
    def __init__(self, cube):
        """
        Initialize the visualizer with a reference to a Cube instance.
        :param cube: Instance of display.cube.Cube
        """
        self.cube = cube
        self.size = CUBE_SIZE

        # Pre-compute grid coordinates
        self.xs, self.ys, self.zs = [], [], []
        for x in range(self.size):
            for y in range(self.size):
                for z in range(self.size):
                    self.xs.append(x)
                    self.ys.append(y)
                    self.zs.append(z)

        self.xs = np.array(self.xs)
        self.ys = np.array(self.ys)
        self.zs = np.array(self.zs)

        # Set up the figure and 3D axis
        self.fig = plt.figure(figsize=(8, 8))
        self.ax = self.fig.add_subplot(111, projection='3d')
        self._configure_axes()

        # Build initial colors
        colors = self._get_colors()

        # Initial scatter plot
        self.scatter = self.ax.scatter(
            self.xs, self.ys, self.zs,
            c=colors,
            s=LED_SIZE,
            depthshade=False,
            edgecolors='none'
        )

    def _configure_axes(self):
        """Style the 3D axes to look clean."""
        self.ax.set_xlim(0, self.size - 1)
        self.ax.set_ylim(0, self.size - 1)
        self.ax.set_zlim(0, self.size - 1)
        self.ax.set_xlabel('X', color='white')
        self.ax.set_ylabel('Y', color='white')
        self.ax.set_zlabel('Z', color='white')
        self.ax.set_title('LED Cube Visualizer', color='white')

        # Set tick positions explicitly so (0,0,0) is a visible corner
        ticks = list(range(self.size))
        self.ax.set_xticks(ticks)
        self.ax.set_yticks(ticks)
        self.ax.set_zticks(ticks)

        self.fig.patch.set_facecolor('#1a1a1a')
        self.ax.set_facecolor('#1a1a1a')
        self.ax.tick_params(colors='white', labelsize=7)
        self.ax.xaxis.pane.fill = False
        self.ax.yaxis.pane.fill = False
        self.ax.zaxis.pane.fill = False
        self.ax.xaxis.pane.set_edgecolor('#444444')
        self.ax.yaxis.pane.set_edgecolor('#444444')
        self.ax.zaxis.pane.set_edgecolor('#444444')

        # Start at a clean viewing angle where (0,0,0) is visible
        self.ax.view_init(elev=20, azim=45)

    def _get_colors(self):
        """Build the color list based on the current cube grid state."""
        grid = self.cube.get_grid()
        colors = []
        for x in range(self.size):
            for y in range(self.size):
                for z in range(self.size):
                    colors.append(LED_ON_COLOR if grid[x][y][z] else LED_OFF_COLOR)
        return colors

    def get_view_angles(self) -> tuple:
        """
        Return the current elevation and azimuth of the 3D view in degrees.
        Used by the virtual gyro to derive a gravity vector from mouse rotation.

        :return: (elev, azim) in degrees
        """
        return self.ax.elev, self.ax.azim

    def _update(self, frame, update_fn):
        """Called each frame — runs the update function then redraws."""
        if update_fn:
            update_fn(frame)
        colors = self._get_colors()
        self.scatter.set_facecolor(colors)
        return (self.scatter,)

    def run(self, update_fn=None, interval=None):
        """
        Start the visualizer loop.
        :param update_fn: Optional function called each frame to update the cube state.
                          Receives the frame number as an argument.
        :param interval:  Milliseconds between frames. Defaults to SIMULATION_SPEED.
        """
        ms = int((interval if interval is not None else SIMULATION_SPEED) * 1000)
        self.ani = animation.FuncAnimation(
            self.fig,
            self._update,
            fargs=(update_fn,),
            interval=ms,
            blit=False
        )
        plt.tight_layout()
        plt.show()