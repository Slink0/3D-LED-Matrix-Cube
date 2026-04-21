"""
mpu_receive.py — Run this on your PC alongside main.py.
Listens for UDP packets from mpu_stream.py running on the Pi
and updates a shared angle state that main.py reads each frame.

This module exposes a single function: get_angles()
Import it in main.py when USE_VIRTUAL_GYRO is False and
you want to use streamed MPU6050 data instead of the physical sensor.

Usage:
    In one terminal: python3 tempStream/mpu_receive.py
    In another:      python3 main.py
"""

import socket
import threading

# ─── Shared State ──────────────────────────────────────────────────────────────
_roll  = 0.0
_pitch = 0.0
_lock  = threading.Lock()
_running = False

# ─── UDP Config ────────────────────────────────────────────────────────────────
DEFAULT_PORT = 5005


def get_angles() -> tuple:
    """
    Return the most recently received roll and pitch angles in degrees.
    Thread safe — can be called from the main simulation loop.

    :return: (roll, pitch) in degrees
    """
    with _lock:
        return _roll, _pitch


def _listen(port: int):
    """Background thread that listens for incoming UDP packets."""
    global _roll, _pitch, _running

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', port))
    sock.settimeout(1.0)

    print(f"[mpu_receive] Listening for MPU6050 stream on port {port}...")
    _running = True

    while _running:
        try:
            data, addr = sock.recvfrom(64)
            parts = data.decode().strip().split(',')
            if len(parts) == 2:
                with _lock:
                    _roll  = float(parts[0])
                    _pitch = float(parts[1])
        except socket.timeout:
            continue
        except Exception as e:
            print(f"[mpu_receive] Error: {e}")

    sock.close()
    print("[mpu_receive] Stopped.")


def start(port: int = DEFAULT_PORT):
    """
    Start the background UDP listener thread.
    Call this once at startup in main.py when using streamed MPU data.

    :param port: UDP port to listen on (must match mpu_stream.py)
    """
    t = threading.Thread(target=_listen, args=(port,), daemon=True)
    t.start()


def stop():
    """Stop the background listener thread."""
    global _running
    _running = False


# ─── Standalone mode ───────────────────────────────────────────────────────────
if __name__ == '__main__':
    import time

    start()
    print("[mpu_receive] Running in standalone mode — printing received angles.")
    print(f"{'Roll (deg)':>15} {'Pitch (deg)':>15}")
    print("-" * 35)

    try:
        while True:
            roll, pitch = get_angles()
            print(f"{roll:>15.2f} {pitch:>15.2f}")
            time.sleep(0.1)
    except KeyboardInterrupt:
        stop()
        print("\n[mpu_receive] Exited.")