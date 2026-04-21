import time
import sys
import os

# Allow imports from the project root
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from hardware.mpu6050 import MPU6050

def main():
    print("Initializing MPU6050...")
    mpu = MPU6050()

    try:
        mpu.connect()
    except ConnectionError as e:
        print(f"Error: {e}")
        sys.exit(1)

    print("Calibrating — keep the MPU6050 still for 2 seconds...")
    mpu.calibrate(samples=250)
    print("Calibration complete.\n")
    print(f"{'Roll (deg)':>15} {'Pitch (deg)':>15} {'Accel X':>10} {'Accel Y':>10} {'Accel Z':>10}")
    print("-" * 65)

    try:
        while True:
            mpu.update()
            roll, pitch = mpu.get_angles()
            ax, ay, az = mpu.get_raw_accel()

            print(f"{roll:>15.2f} {pitch:>15.2f} {ax:>10.3f} {ay:>10.3f} {az:>10.3f}")
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nStopped.")

if __name__ == '__main__':
    main()