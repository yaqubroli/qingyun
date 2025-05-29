#!/usr/bin/env python3

import os
import csv
import re

BASE_DIR = "/sys/kernel/debug/opp"
FIELDS = ["u_volt_min", "u_volt_max", "u_volt_target", "u_amp", "u_watt"]
CSV_OUTPUT = "opp_voltage_report.csv"

def read_value(file_path):
    try:
        with open(file_path, "r") as f:
            return int(f.read().strip())
    except:
        return None

def extract_opp_freq(path):
    """Extracts OPP frequency from directory name"""
    match = re.search(r"/opp:(\d+)", path)
    if match:
        freq = int(match.group(1))
        return freq, hex(freq)
    return "", ""

def main():
    rows = []

    # Only look at entries like cpu0, cpu1, etc.
    for entry in os.listdir(BASE_DIR):
        if not re.fullmatch(r"cpu\d+", entry):
            continue

        logical_cpu_path = os.path.join(BASE_DIR, entry)
        try:
            # Resolve symlink
            real_cpu_path = os.path.realpath(logical_cpu_path)
        except:
            continue

        # Walk the real path
        for root, dirs, files in os.walk(real_cpu_path):
            if "/supply-0" in root:
                data = {}
                for field in FIELDS:
                    full_path = os.path.join(root, field)
                    val = read_value(full_path)
                    if val is not None:
                        data[field] = (val, hex(val))
                    else:
                        data[field] = ("", "")
                
                freq_dec, freq_hex = extract_opp_freq(root)
                # Reconstruct logical path by replacing the real path prefix with the logical one
                logical_root = root.replace(real_cpu_path, logical_cpu_path, 1)
                rows.append([entry, logical_root, freq_dec, freq_hex] + [val for field in FIELDS for val in data[field]])

    header = ["CPU", "Path", "opp_freq_dec", "opp_freq_hex"]
    for field in FIELDS:
        header += [f"{field}_dec", f"{field}_hex"]

    with open(CSV_OUTPUT, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)
        writer.writerows(rows)

    print(f"CSV output written to: {CSV_OUTPUT}")

if __name__ == "__main__":
    main()
