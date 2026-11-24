#!/usr/bin/env python3
"""
Plot vehRoll, vehPitch, and vehHeading from UBX-NAV-PVAT log lines like:
  sensormanager: ...[UBX-NAV-PVAT ... vehRoll=0.14072 vehPitch=4.02714 vehHeading=56.2498 ...]
"""

import math
import re
import sys
import argparse
import matplotlib.pyplot as plt

# Matches UBX-NAV-PVAT lines and captures the key=value payload
LOG_PATTERN = re.compile(r'\[UBX-NAV-PVAT\s+(.*?)\]')

# Extract specific fields
FIELD_PATTERNS = {
    'vehRoll': re.compile(r'vehRoll=([\-\d\.eEnNaAiIfF]+)'),
    'vehPitch': re.compile(r'vehPitch=([\-\d\.eEnNaAiIfF]+)'),
    'vehHeading': re.compile(r'vehHeading=([\-\d\.eEnNaAiIfF]+)'),
}


def parse_log(filepath: str):
    """Parse log and extract vehRoll, vehPitch, vehHeading synchronously.
    Only keeps samples where ALL fields are valid.
    """
    timestamps = []
    roll_vals = []
    pitch_vals = []
    heading_vals = []
    sample_count = 0

    with open(filepath, 'r', errors='replace') as f:
        for lineno, line in enumerate(f, start=1):
            m = LOG_PATTERN.search(line)
            if not m:
                continue
            payload = m.group(1)

            # Extract all three fields
            parsed = {}
            valid = True
            for name, pat in FIELD_PATTERNS.items():
                fm = pat.search(payload)
                if not fm:
                    valid = False
                    break
                try:
                    value = float(fm.group(1))
                except ValueError:
                    valid = False
                    break
                if math.isnan(value) or math.isinf(value):
                    valid = False
                    break
                parsed[name] = value

            if not valid:
                continue

            timestamps.append(sample_count)
            roll_vals.append(parsed['vehRoll'])
            pitch_vals.append(parsed['vehPitch'])
            heading_vals.append(parsed['vehHeading'])
            sample_count += 1

    return timestamps, roll_vals, pitch_vals, heading_vals


def main():
    parser = argparse.ArgumentParser(
        description="Plot vehRoll, vehPitch, vehHeading from UBX-NAV-PVAT log lines."
    )
    parser.add_argument('logfile', help="Path to the log file")
    parser.add_argument(
        '--output', default=None,
        help="Save plot to file instead of displaying (e.g. output.png)"
    )
    parser.add_argument(
        '--title', default="Vehicle Pitch/Roll/Yaw (UBX-NAV-PVAT)",
        help="Plot title"
    )
    args = parser.parse_args()

    timestamps, roll_vals, pitch_vals, heading_vals = parse_log(args.logfile)

    if not timestamps:
        print("No matching UBX-NAV-PVAT log lines found.", file=sys.stderr)
        sys.exit(1)

    print(f"Parsed {len(timestamps)} samples.")
    print(f"  vehRoll:    Min={min(roll_vals):.5f}  Max={max(roll_vals):.5f}  Mean={sum(roll_vals)/len(roll_vals):.5f}")
    print(f"  vehPitch:   Min={min(pitch_vals):.5f}  Max={max(pitch_vals):.5f}  Mean={sum(pitch_vals)/len(pitch_vals):.5f}")
    print(f"  vehHeading: Min={min(heading_vals):.5f}  Max={max(heading_vals):.5f}  Mean={sum(heading_vals)/len(heading_vals):.5f}")

    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10), sharex=True)

    # vehRoll
    ax1.plot(timestamps, roll_vals, linewidth=0.8, color='steelblue', label='vehRoll')
    ax1.axhline(0, color='gray', linewidth=0.6, linestyle='--')
    ax1.set_ylabel("Roll (deg)")
    ax1.set_title(args.title)
    ax1.legend()
    ax1.grid(True, alpha=0.4)

    # vehPitch
    ax2.plot(timestamps, pitch_vals, linewidth=0.8, color='crimson', label='vehPitch')
    ax2.axhline(0, color='gray', linewidth=0.6, linestyle='--')
    ax2.set_ylabel("Pitch (deg)")
    ax2.legend()
    ax2.grid(True, alpha=0.4)

    # vehHeading
    ax3.plot(timestamps, heading_vals, linewidth=0.8, color='darkorange', label='vehHeading')
    ax3.set_xlabel("Sample index")
    ax3.set_ylabel("Heading (deg)")
    ax3.legend()
    ax3.grid(True, alpha=0.4)

    fig.tight_layout()

    if args.output:
        fig.savefig(args.output, dpi=150)
        print(f"Plot saved to {args.output}")
    else:
        plt.show()


if __name__ == '__main__':
    main()
