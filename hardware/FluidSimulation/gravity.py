import numpy as np
class GravityVector:
    def __init__(self):
        """
        Manages the gravity vector used by the fluid simulation.
        Gravity is expressed as a normalized 3D direction vector scaled by G.
        Default is straight down along the -Z axis.
        """
        self._gravity = np.array([0.0, 0.0, -9.8])

    def set_from_angles(self, roll_deg: float, pitch_deg: float):
        """
        Update the gravity vector from roll and pitch angles in degrees.
        This is how tilt data from the MPU6050 will be passed in.

        Roll  — rotation around the X axis (tilting left/right)
        Pitch — rotation around the Y axis (tilting forward/back)

        :param roll_deg:  Roll angle in degrees
        :param pitch_deg: Pitch angle in degrees
        """
        roll = np.radians(roll_deg)
        pitch = np.radians(pitch_deg)

        # Decompose gravity into XYZ components based on tilt
        gx = np.sin(pitch)
        gy = -np.sin(roll) * np.cos(pitch)
        gz = -np.cos(roll) * np.cos(pitch)

        magnitude = np.sqrt(gx**2 + gy**2 + gz**2)
        if magnitude > 0:
            self._gravity = np.array([gx, gy, gz]) / magnitude * 9.8
        else:
            self._gravity = np.array([0.0, 0.0, -9.8])

    def set_from_visualizer(self, elev_deg: float, azim_deg: float):
        """
        Update the gravity vector from matplotlib axis elevation and azimuth.
        Used when USE_VIRTUAL_GYRO is True during development.

        :param elev_deg: Elevation angle from matplotlib ax.elev
        :param azim_deg: Azimuth angle from matplotlib ax.azim
        """
        elev = np.radians(elev_deg)
        azim = np.radians(azim_deg)

        # Convert spherical viewing angles to a gravity direction
        gx = np.cos(elev) * np.sin(azim)
        gy = np.cos(elev) * np.cos(azim)
        gz = -np.sin(elev)

        magnitude = np.sqrt(gx**2 + gy**2 + gz**2)
        if magnitude > 0:
            self._gravity = np.array([gx, gy, gz]) / magnitude * 9.8
        else:
            self._gravity = np.array([0.0, 0.0, -9.8])

    def set_raw(self, gx: float, gy: float, gz: float):
        """
        Directly set the gravity vector components.
        Useful for testing or passing in raw MPU6050 accelerometer data.

        :param gx: Gravity X component
        :param gy: Gravity Y component
        :param gz: Gravity Z component
        """
        vec = np.array([gx, gy, gz], dtype=float)
        magnitude = np.linalg.norm(vec)
        if magnitude > 0:
            self._gravity = vec / magnitude * 9.8
        else:
            self._gravity = np.array([0.0, 0.0, -9.8])

    def get(self) -> np.ndarray:
        """Return the current gravity vector as a numpy array."""
        return self._gravity.copy()