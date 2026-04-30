#!/usr/bin/env python3
"""
Plot accelerometer (Sensor: 1) and gyroscope (Sensor: 4) X, Y, Z values from log lines like:
  Sensor: 1, Received data :: -1.378231:0.513437:9.759488, 5134924768143
  Sensor: 4, Received data :: 0.001234:-0.002345:0.003456, 5134924768143
"""

import math
import re
import sys
import argparse
import matplotlib.pyplot as plt

# Matches "Sensor: <id>, Received data :: <x>:<y>:<z>, <timestamp>"
# Requires a comma after z (not colon/space), so timestamp is ignored
LOG_PATTERN = re.compile(
    r'Sensor:\s*(\d+)\b,\s*Received data\s*::\s*([\w\d\.\-\+eE]+):([\w\d\.\-\+eE]+):([\w\d\.\-\+eE]+),'
)

ACCEL_SENSOR_ID = 1
GYRO_SENSOR_ID = 4


def parse_log(filepath: str):
    """Parse log and extract X, Y, Z for accelerometer and gyroscope."""
    accel = {'ts': [], 'x': [], 'y': [], 'z': []}
    gyro = {'ts': [], 'x': [], 'y': [], 'z': []}
    accel_count = 0
    gyro_count = 0

    with open(filepath, 'r', errors='replace') as f:
        for lineno, line in enumerate(f, start=1):
            for m in LOG_PATTERN.finditer(line):
                sensor_id = int(m.group(1))
                if sensor_id not in (ACCEL_SENSOR_ID, GYRO_SENSOR_ID):
                    continue

                try:
                    x = float(m.group(2))
                    y = float(m.group(3))
                    z = float(m.group(4))
                except ValueError:
                    continue

                if any(math.isnan(v) or math.isinf(v) for v in (x, y, z)):
                    continue

                if sensor_id == ACCEL_SENSOR_ID:
                    accel['ts'].append(accel_count)
                    accel['x'].append(x)
                    accel['y'].append(y)
                    accel['z'].append(z)
                    accel_count += 1
                elif sensor_id == GYRO_SENSOR_ID:
                    gyro['ts'].append(gyro_count)
                    gyro['x'].append(x)
                    gyro['y'].append(y)
                    gyro['z'].append(z)
                    gyro_count += 1

    return accel, gyro


def print_stats(name, data):
    n = len(data['x'])
    if n == 0:
        print(f"  {name}: no samples")
        return
    print(f"  {name}: {n} samples")
    for axis in ('x', 'y', 'z'):
        vals = data[axis]
        print(f"    {axis}: Min={min(vals):.6f}  Max={max(vals):.6f}  Mean={sum(vals)/len(vals):.6f}")


def main():
    parser = argparse.ArgumentParser(
        description="Plot accelerometer (Sensor 1) and gyroscope (Sensor 4) X/Y/Z from IVI sensor log."
    )
    parser.add_argument('logfile', help="Path to the log file")
    parser.add_argument(
        '--output', default=None,
        help="Save plot to file instead of displaying (e.g. output.png)"
    )
    parser.add_argument(
        '--title', default="IVI Sensor Data",
        help="Plot title"
    )
    args = parser.parse_args()

    accel, gyro = parse_log(args.logfile)

    if not accel['x'] and not gyro['x']:
        print("No matching sensor log lines found.", file=sys.stderr)
        sys.exit(1)

    print(f"Parsed sensor data:")
    print_stats("Accelerometer (Sensor 1)", accel)
    print_stats("Gyroscope (Sensor 4)", gyro)

    # Figure 1: Accelerometer
    if accel['x']:
        fig1, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 8), sharex=True)
        fig1.suptitle(f"{args.title} — Accelerometer (Sensor 1)")

        ax1.plot(accel['ts'], accel['x'], linewidth=0.6, color='steelblue')
        ax1.axhline(0, color='gray', linewidth=0.5, linestyle='--')
        ax1.set_ylabel("Accel X (m/s²)")
        ax1.grid(True, alpha=0.4)

        ax2.plot(accel['ts'], accel['y'], linewidth=0.6, color='darkorange')
        ax2.axhline(0, color='gray', linewidth=0.5, linestyle='--')
        ax2.set_ylabel("Accel Y (m/s²)")
        ax2.grid(True, alpha=0.4)

        ax3.plot(accel['ts'], accel['z'], linewidth=0.6, color='forestgreen')
        ax3.axhline(0, color='gray', linewidth=0.5, linestyle='--')
        ax3.set_ylabel("Accel Z (m/s²)")
        ax3.set_xlabel("Sample index")
        ax3.grid(True, alpha=0.4)

        fig1.tight_layout()

        if args.output:
            accel_path = args.output.replace('.png', '_accel.png')
            fig1.savefig(accel_path, dpi=150)
            print(f"Accelerometer plot saved to {accel_path}")

    # Figure 2: Gyroscope
    if gyro['x']:
        fig2, (ax4, ax5, ax6) = plt.subplots(3, 1, figsize=(12, 8), sharex=True)
        fig2.suptitle(f"{args.title} — Gyroscope (Sensor 4)")

        ax4.plot(gyro['ts'], gyro['x'], linewidth=0.6, color='steelblue')
        ax4.axhline(0, color='gray', linewidth=0.5, linestyle='--')
        ax4.set_ylabel("Gyro X (rad/s)")
        ax4.grid(True, alpha=0.4)

        ax5.plot(gyro['ts'], gyro['y'], linewidth=0.6, color='darkorange')
        ax5.axhline(0, color='gray', linewidth=0.5, linestyle='--')
        ax5.set_ylabel("Gyro Y (rad/s)")
        ax5.grid(True, alpha=0.4)

        ax6.plot(gyro['ts'], gyro['z'], linewidth=0.6, color='forestgreen')
        ax6.axhline(0, color='gray', linewidth=0.5, linestyle='--')
        ax6.set_ylabel("Gyro Z (rad/s)")
        ax6.set_xlabel("Sample index")
        ax6.grid(True, alpha=0.4)

        fig2.tight_layout()

        if args.output:
            gyro_path = args.output.replace('.png', '_gyro.png')
            fig2.savefig(gyro_path, dpi=150)
            print(f"Gyroscope plot saved to {gyro_path}")

    if not args.output:
        plt.show()


if __name__ == '__main__':
    main()
