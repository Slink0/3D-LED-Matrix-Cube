"""
mpu_stream.py — Run this on the Raspberry Pi.
Reads roll and pitch from the MPU6050 and broadcasts them over UDP
to a target PC running mpu_receive.py.

Usage:
    python3 tempStream/mpu_stream.py --host 192.168.1.x --port 5005
"""

import socket
import time
import sys
import os
import argparse

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from hardware.mpu6050 import MPU6050


def main():
    parser = argparse.ArgumentParser(description='Stream MPU6050 angles over UDP')
    parser.add_argument('--host', type=str, required=True,
                        help='IP address of the PC running mpu_receive.py')
    parser.add_argument('--port', type=int, default=5005,
                        help='UDP port to stream on (default: 5005)')
    args = parser.parse_args()

    print(f"[mpu_stream] Targeting {args.host}:{args.port}")

    # Initialize MPU6050
    mpu = MPU6050()
    try:
        mpu.connect()
    except ConnectionError as e:
        print(f"[mpu_stream] Error connecting to MPU6050: {e}")
        sys.exit(1)

    print("[mpu_stream] Calibrating — keep the sensor still...")
    mpu.calibrate(samples=200)
    print("[mpu_stream] Calibration complete. Streaming angles...\n")

    # Set up UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        while True:
            mpu.update()
            roll, pitch = mpu.get_angles()

            # Send as a simple comma separated string
            message = f"{roll:.4f},{pitch:.4f}"
            sock.sendto(message.encode(), (args.host, args.port))

            print(f"[mpu_stream] roll={roll:.2f} pitch={pitch:.2f}")
            time.sleep(0.05)  # 20hz stream

    except KeyboardInterrupt:
        print("\n[mpu_stream] Stopped.")
    finally:
        sock.close()


if __name__ == '__main__':
    main()