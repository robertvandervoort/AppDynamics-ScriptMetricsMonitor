#!/usr/bin/env python3
import sys
import os
from datetime import datetime
import json
import psutil

# Define the filename for persistent storage
PERSISTENCE_FILE = "cpu_stats_last_values.json"

def get_cpu_stats_json():
    """Retrieves CPU stats and formats them as JSON."""
    cpu_stats = psutil.cpu_stats()
    
    if os.name == "nt":
        metrics = {
            "ctx_switches": cpu_stats.ctx_switches,
            "interrupts": cpu_stats.interrupts,
            "syscalls": cpu_stats.syscalls,
            "timestamp": datetime.now().isoformat()  # Store timestamp for comparison
        }
    
    else:
        metrics = {
            "ctx_switches": cpu_stats.ctx_switches,
            "interrupts": cpu_stats.interrupts,
            "soft_interrupts": cpu_stats.soft_interrupts,
            "syscalls": cpu_stats.syscalls,
            "timestamp": datetime.now().isoformat()  # Store timestamp for comparison
        }

    return json.dumps(metrics, indent=4)

def calculate_differences(current_data, last_data):
    """Calculates differences between current and last data points,
    then converts them to per-second values. Handles counter resets accurately."""
    differences = {}
    last_timestamp = datetime.fromisoformat(last_data["timestamp"])
    current_timestamp = datetime.fromisoformat(current_data["timestamp"])
    time_difference = (current_timestamp - last_timestamp).total_seconds()

    # Assuming a 32-bit counter (modify if different)
    max_counter_value = 2**32 - 1

    for metric in current_data:
        if metric != "timestamp":
            diff = current_data[metric] - last_data[metric]
            if diff < 0:  # Counter reset detected
                # Account for the difference between max counter value and the last value
                diff += (max_counter_value - last_data[metric]) + 1 

            differences[metric] = int(diff // time_difference)  # Per-second value as integer

    return differences

if __name__ == "__main__":
    current_data = json.loads(get_cpu_stats_json())

    if os.path.exists(PERSISTENCE_FILE):
        with open(PERSISTENCE_FILE, 'r') as f:
            last_data = json.load(f)

        differences = calculate_differences(current_data, last_data)
        print(json.dumps(differences, indent=4), flush=True)

    else:
        # If the file doesn't exist, create it and write the initial data
        pass

    # Update the persistence file with the latest data
    with open(PERSISTENCE_FILE, 'w') as f:
        json.dump(current_data, f, indent=4)

    sys.exit()