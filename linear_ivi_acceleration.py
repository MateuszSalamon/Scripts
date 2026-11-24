#!/usr/bin/env python3
"""
Plot linear acceleration (field 7), speed (field 4), and altitude (field 3)
from log lines like:
  onEventSendProbeData() : [100] 1777029439,35638178,139758437,52.080002,61.310459,315.115601,-0.185930,0.062851,4.372782,1
"""

import math
import re
import sys
import argparse
import matplotlib.pyplot as plt

# Matches the data portion after the bracket, e.g. "[100] val0,val1,...,val9"
# Also accepts nan/inf/-inf in fields
LOG_PATTERN = re.compile(
    r'onEventSendProbeData\(\)\s*:\s*\[\d+\]\s*([\w\d\-\.]+(?:,[\w\d\-\.]+)+)',
    re.IGNORECASE
)

# Zero-based field indices
FIELD_INDEX = 7          # linear acceleration
ACCEL_FIELD_INDEX = 6    # acceleration
ALTITUDE_FIELD_INDEX = 3 # altitude
SPEED_FIELD_INDEX = 4    # speed


def parse_log(filepath: str, field_indices: list):
    """Parse log and extract multiple fields synchronously.
    Only keeps samples where ALL requested fields are valid (no NaN/Inf/parse errors).
    Returns dict of {index: (timestamps, values)} with aligned sample indices.
    """
    results = {idx: ([], []) for idx in field_indices}
    sample_count = 0

    with open(filepath, 'r', errors='replace') as f:
        for lineno, line in enumerate(f, start=1):
            m = LOG_PATTERN.search(line)
            if not m:
                continue
            fields = m.group(1).split(',')

            # Parse all requested fields for this line
            parsed = {}
            valid = True
            for idx in field_indices:
                if len(fields) <= idx:
                    valid = False
                    break
                try:
                    value = float(fields[idx])
                except ValueError:
                    valid = False
                    break
                if math.isnan(value) or math.isinf(value):
                    valid = False
                    break
                parsed[idx] = value

            if not valid:
                continue

            # All fields valid — store them with the same sample index
            for idx in field_indices:
                ts_list, val_list = results[idx]
                ts_list.append(sample_count)
                val_list.append(parsed[idx])
            sample_count += 1

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Plot linear acceleration (field 8) from onEventSendProbeData() log lines."
    )
    parser.add_argument('logfile', help="Path to the log file")
    parser.add_argument(
        '--field', type=int, default=FIELD_INDEX,
        help=f"Zero-based field index for linear acceleration (default: {FIELD_INDEX})"
    )
    parser.add_argument(
        '--speed-field', type=int, default=SPEED_FIELD_INDEX,
        help=f"Zero-based field index for speed (default: {SPEED_FIELD_INDEX})"
    )
    parser.add_argument(
        '--altitude-field', type=int, default=ALTITUDE_FIELD_INDEX,
        help=f"Zero-based field index for altitude (default: {ALTITUDE_FIELD_INDEX})"
    )
    parser.add_argument(
        '--accel-field', type=int, default=ACCEL_FIELD_INDEX,
        help=f"Zero-based field index for acceleration (default: {ACCEL_FIELD_INDEX})"
    )
    parser.add_argument(
        '--output', default=None,
        help="Save plot to file instead of displaying (e.g. output.png)"
    )
    parser.add_argument(
        '--title', default="Linear Acceleration",
        help="Plot title"
    )
    args = parser.parse_args()

    field_index = args.field
    speed_index = args.speed_field
    altitude_index = args.altitude_field
    accel_index = args.accel_field

    results = parse_log(args.logfile, [field_index, speed_index, altitude_index, accel_index])
    lin_accel_ts, lin_accel_vals = results[field_index]
    speed_ts, speed_vals = results[speed_index]
    alt_ts, alt_vals = results[altitude_index]
    accel_ts, accel_vals = results[accel_index]

    if not lin_accel_vals and not speed_vals and not alt_vals and not accel_vals:
        print("No matching log lines found.", file=sys.stderr)
        sys.exit(1)

    if lin_accel_vals:
        print(f"Lin Accel (field {field_index}): {len(lin_accel_vals)} samples, Min={min(lin_accel_vals):.6f}  Max={max(lin_accel_vals):.6f}  Mean={sum(lin_accel_vals)/len(lin_accel_vals):.6f}")
    if accel_vals:
        print(f"Accel     (field {accel_index}): {len(accel_vals)} samples, Min={min(accel_vals):.6f}  Max={max(accel_vals):.6f}  Mean={sum(accel_vals)/len(accel_vals):.6f}")
    if speed_vals:
        print(f"Speed     (field {speed_index}): {len(speed_vals)} samples, Min={min(speed_vals):.6f}  Max={max(speed_vals):.6f}  Mean={sum(speed_vals)/len(speed_vals):.6f}")
    if alt_vals:
        print(f"Altitude  (field {altitude_index}): {len(alt_vals)} samples, Min={min(alt_vals):.6f}  Max={max(alt_vals):.6f}  Mean={sum(alt_vals)/len(alt_vals):.6f}")

    fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, figsize=(12, 12), sharex=True)

    # Linear acceleration plot
    ax1.plot(lin_accel_ts, lin_accel_vals, linewidth=0.8, color='steelblue', label=f'Lin Accel (field {field_index})')
    ax1.axhline(0, color='gray', linewidth=0.6, linestyle='--')
    ax1.set_ylabel("Linear Acceleration")
    ax1.set_title(args.title)
    ax1.legend()
    ax1.grid(True, alpha=0.4)

    # Acceleration plot
    ax2.plot(accel_ts, accel_vals, linewidth=0.8, color='crimson', label=f'Accel (field {accel_index})')
    ax2.axhline(0, color='gray', linewidth=0.6, linestyle='--')
    ax2.set_ylabel("Acceleration")
    ax2.legend()
    ax2.grid(True, alpha=0.4)

    # Speed plot
    ax3.plot(speed_ts, speed_vals, linewidth=0.8, color='darkorange', label=f'Speed (field {speed_index})')
    ax3.axhline(0, color='gray', linewidth=0.6, linestyle='--')
    ax3.set_ylabel("Speed")
    ax3.legend()
    ax3.grid(True, alpha=0.4)

    # Altitude plot
    ax4.plot(alt_ts, alt_vals, linewidth=0.8, color='forestgreen', label=f'Altitude (field {altitude_index})')
    ax4.set_xlabel("Sample index")
    ax4.set_ylabel("Altitude")
    ax4.legend()
    ax4.grid(True, alpha=0.4)

    fig.tight_layout()

    if args.output:
        fig.savefig(args.output, dpi=150)
        print(f"Plot saved to {args.output}")
    else:
        plt.show()


if __name__ == '__main__':
    main()
