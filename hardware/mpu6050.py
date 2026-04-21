import time
import numpy as np

# MPU6050 register addresses
_REG_PWR_MGMT_1   = 0x6B
_REG_ACCEL_XOUT_H = 0x3B
_REG_GYRO_XOUT_H  = 0x43
_REG_CONFIG       = 0x1A
_REG_GYRO_CONFIG  = 0x1B
_REG_ACCEL_CONFIG = 0x1C

# Sensitivity scale factors (datasheet values)
_ACCEL_SCALE = 16384.0  # LSB/g  for ±2g range
_GYRO_SCALE  = 131.0    # LSB/(°/s) for ±250°/s range


class MPU6050:
    def __init__(self, i2c_address=0x68, alpha=0.98):
        """
        Interface for the MPU6050 accelerometer and gyroscope.
        Uses a complementary filter to produce stable roll and pitch angles.

        The complementary filter blends:
          - Gyroscope:     accurate short term, drifts long term
          - Accelerometer: noisy short term, stable long term

        Formula each frame:
            angle = alpha * (angle + gyro_rate * dt) + (1 - alpha) * accel_angle

        :param i2c_address: I2C address of the MPU6050 (default 0x68)
        :param alpha:       Complementary filter coefficient (default 0.98)
                            Higher = trust gyro more, lower = trust accelerometer more
        """
        self.address = i2c_address
        self.alpha = alpha
        self.bus = None

        # Integrated angles in degrees
        self.roll  = 0.0
        self.pitch = 0.0

        # Gyroscope bias calibration offsets (degrees/s)
        self._gyro_bias = np.zeros(3)

        self._last_time = None

    # ─── Setup ─────────────────────────────────────────────────────────────────

    def connect(self):
        """
        Initialize the I2C bus and wake the MPU6050 from sleep mode.
        Must be called before any reads.
        """
        try:
            import smbus2
            self.bus = smbus2.SMBus(1)  # I2C bus 1 on Raspberry Pi
            # Wake the MPU6050 — it starts in sleep mode by default
            self.bus.write_byte_data(self.address, _REG_PWR_MGMT_1, 0x00)
            time.sleep(0.1)
            self._last_time = time.time()
            print(f"MPU6050 connected at address 0x{self.address:02X}")
        except Exception as e:
            raise ConnectionError(f"Failed to connect to MPU6050: {e}")

    def calibrate(self, samples=200):
        """
        Measure gyroscope bias while the cube is stationary.
        Should be called once at startup before movement begins.
        The cube must be completely still during calibration.

        :param samples: Number of samples to average for bias estimation
        """
        print("Calibrating gyroscope — keep the cube still...")
        bias = np.zeros(3)
        for _ in range(samples):
            gx, gy, gz = self._read_gyro_raw()
            bias += np.array([gx, gy, gz])
            time.sleep(0.005)
        self._gyro_bias = bias / samples
        print(f"Calibration complete. Bias: {self._gyro_bias}")

    # ─── Raw Reads ─────────────────────────────────────────────────────────────

    def _read_raw_word(self, reg: int) -> int:
        """Read a signed 16-bit value from two consecutive registers."""
        high = self.bus.read_byte_data(self.address, reg)
        low  = self.bus.read_byte_data(self.address, reg + 1)
        value = (high << 8) | low
        # Convert to signed
        if value >= 0x8000:
            value -= 0x10000
        return value

    def _read_accel_raw(self) -> tuple:
        """Return raw accelerometer values (ax, ay, az) in g."""
        ax = self._read_raw_word(_REG_ACCEL_XOUT_H)     / _ACCEL_SCALE
        ay = self._read_raw_word(_REG_ACCEL_XOUT_H + 2) / _ACCEL_SCALE
        az = self._read_raw_word(_REG_ACCEL_XOUT_H + 4) / _ACCEL_SCALE
        return ax, ay, az

    def _read_gyro_raw(self) -> tuple:
        """Return raw gyroscope values (gx, gy, gz) in degrees/s."""
        gx = self._read_raw_word(_REG_GYRO_XOUT_H)     / _GYRO_SCALE
        gy = self._read_raw_word(_REG_GYRO_XOUT_H + 2) / _GYRO_SCALE
        gz = self._read_raw_word(_REG_GYRO_XOUT_H + 4) / _GYRO_SCALE
        return gx, gy, gz

    # ─── Complementary Filter ──────────────────────────────────────────────────

    def _accel_angles(self, ax: float, ay: float, az: float) -> tuple:
        """
        Derive roll and pitch from accelerometer data.
        These are stable long term but noisy each frame.

        :return: (roll_deg, pitch_deg)
        """
        roll  = np.degrees(np.arctan2(ay, az))
        pitch = np.degrees(np.arctan2(-ax, np.sqrt(ay**2 + az**2)))
        return roll, pitch

    def update(self):
        """
        Read sensors and run the complementary filter to update roll and pitch.
        Should be called once per simulation frame.
        """
        now = time.time()
        dt = now - self._last_time
        self._last_time = now

        # Read both sensors
        ax, ay, az = self._read_accel_raw()
        gx, gy, gz = self._read_gyro_raw()

        # Subtract calibration bias from gyro readings
        gx -= self._gyro_bias[0]
        gy -= self._gyro_bias[1]
        gz -= self._gyro_bias[2]

        # Accelerometer derived angles (stable, noisy)
        accel_roll, accel_pitch = self._accel_angles(ax, ay, az)

        # Complementary filter:
        # Trust gyro integration for fast motion, correct drift with accelerometer
        self.roll  = self.alpha * (self.roll  + gx * dt) + (1 - self.alpha) * accel_roll
        self.pitch = self.alpha * (self.pitch + gy * dt) + (1 - self.alpha) * accel_pitch

    # ─── Output ────────────────────────────────────────────────────────────────

    def get_angles(self) -> tuple:
        """
        Return the current filtered roll and pitch angles in degrees.
        Feed these directly into GravityVector.set_from_angles().

        :return: (roll_deg, pitch_deg)
        """
        return self.roll, self.pitch

    def get_raw_accel(self) -> tuple:
        """Return raw accelerometer values in g for debugging."""
        return self._read_accel_raw()

    def get_raw_gyro(self) -> tuple:
        """Return raw gyroscope values in degrees/s for debugging."""
        gx, gy, gz = self._read_gyro_raw()
        return (
            gx - self._gyro_bias[0],
            gy - self._gyro_bias[1],
            gz - self._gyro_bias[2]
        )