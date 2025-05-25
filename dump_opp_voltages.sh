#!/bin/bash

OUTPUT_FILE="opp_voltages.csv"
BASE_PATH="/sys/kernel/debug/opp"

# Write header
echo "cpu,frequency_hz,u_volt_min,u_volt_target,u_volt_max,u_amp,u_watt,path" > "$OUTPUT_FILE"

# Iterate through all OPP supply directories
find "$BASE_PATH" -type d -path "*/cpu*/opp:*/supply-0" | while read -r dir; do
    # Parse CPU name (cpu0, cpu1, etc.)
    cpu=$(echo "$dir" | grep -o "cpu[0-9]\+")

    # Parse frequency from the parent opp:* directory
    freq=$(basename "$(dirname "$dir")" | sed 's/opp://')

    # Safely extract values, or set to N/A if not available
    vmin=$(cat "$dir/u_volt_min" 2>/dev/null || echo "N/A")
    vtarget=$(cat "$dir/u_volt_target" 2>/dev/null || echo "N/A")
    vmax=$(cat "$dir/u_volt_max" 2>/dev/null || echo "N/A")
    uamp=$(cat "$dir/u_amp" 2>/dev/null || echo "N/A")
    uwatt=$(cat "$dir/u_watt" 2>/dev/null || echo "N/A")

    # Write data to CSV
    echo "$cpu,$freq,$vmin,$vtarget,$vmax,$uamp,$uwatt,$dir" >> "$OUTPUT_FILE"
done

echo "Voltage data written to $OUTPUT_FILE"
