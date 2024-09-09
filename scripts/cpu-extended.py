#!/usr/bin/env python3
import sys
import json
import psutil

def get_cpu_stats_json():
    """Retrieves CPU stats and formats them as JSON."""

    cpu_stats = psutil.cpu_stats()

    # Create a dictionary for relevant metrics only
    metrics = {
        "ctx_switches": cpu_stats.ctx_switches,
        "interrupts": cpu_stats.interrupts,
        "soft_interrupts": cpu_stats.soft_interrupts,
        "syscalls": cpu_stats.syscalls,
    }

    # Convert to JSON
    json_data = json.dumps(metrics, indent=4)
    return json_data

if __name__ == "__main__":
    json_output = get_cpu_stats_json()
    print(json_output, flush=True)  # Print to console for AppDynamics
    sys.exit()