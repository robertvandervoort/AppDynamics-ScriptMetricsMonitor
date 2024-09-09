#!/usr/bin/env python3

import os #used for fixing pathnames in script config
import sys
import contextlib
import xml.etree.ElementTree as ET
import subprocess
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import yaml
from appd_metric_collector.appd_metric_collector import AppDMetricCollector

def execute_script(job):
    """Executes a single script based on its configuration."""
    script_path = repr(job['script'])[1:-1]  # Convert to raw string
    script_path = os.path.normpath(script_path)

    try:
        if script_path.endswith('.py'):
            if sys.version_info >= (3, 7):
                #do it this way for Windows using either cmd.exe or shell=true or the agent wont capture the output
                if os.name == "nt":
                    result = subprocess.run(['cmd.exe', '/c', f'python {script_path}'], capture_output=True, text=True, check=False, timeout=55)
                else:
                    result = subprocess.run(['python', script_path], capture_output=True, text=True, check=False, timeout=55)
                if result.returncode != 0:
                    print(f"Error executing child script: {result.stderr}")
            else:
                result = subprocess.run(['python', script_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=0, check=False, timeout=55)
                if result.returncode != 0:
                    print(f"Error executing child script: {result.stderr}")

        elif script_path.endswith('.exe'):
            result = subprocess.check_output([script_path, "-q", "-x"], universal_newlines=True, timeout=55)
            if result.returncode != 0:
                print(f"Error executing child script: {result.stderr}")

        elif script_path.endswith(('.cmd', '.bat', '.sh')):
            result = subprocess.run([script_path], capture_output=True, text=True, bufsize=0, check=False, timeout=60)
            if result.returncode != 0:
                    print(f"Error executing child script: {result.stderr}")

        else:
            if sys.version_info >= (3, 7):
                result = subprocess.run([script_path], capture_output=True, text=True, bufsize=0, check=False, timeout=60)
                if result.returncode != 0:
                    print(f"Error executing child script: {result.stderr}")
            else:
                with contextlib.closing(subprocess.Popen([script_path], stdout=subprocess.PIPE, bufsize=0)) as proc:
                    result = proc.stdout.read().decode()
                if result.returncode != 0:
                    print(f"Error executing child script: {result.stderr}")

        return result.stdout  # Return the standard output
    
    except subprocess.TimeoutExpired:
        print("Child script timed out.")
    
    except subprocess.CalledProcessError as e:
        print("Error executing command:", e)
        return None

    except Exception as e:
        print(f"Error processing job '{job['name']}': {e}")
        return None  # Indicate an error occurred

def parse_and_collect_metrics(job, output, collector, global_metric_path):
    """Parses the script output, renames metrics (if needed), and collects them."""
    metrics = {}
    if job['output_format'] == 'json':
        metrics = json.loads(output)
    
    elif job['output_format'] == 'xml':
        root = ET.fromstring(output)
        metrics = {elem.tag: elem.text for elem in root.iter()}
    
    else:  # keyvalue or key=value
        for line in output.splitlines():
            key, value = line.split('=', 1) if '=' in line else line.split(None, 1)
            metrics[key.strip()] = value.strip()

    if 'metrics' in job:
        for mapping in job['metrics']:
            if mapping['original_name'] in metrics:
                metrics[mapping['metric_name']] = metrics.pop(mapping['original_name'])

    metric_path = job.get('metric_path', global_metric_path)
    collector.collect_metrics(metric_path, job['name'], metrics)

def main():
    """Main program code"""
    with open("config.yml", 'r') as f:
        config = yaml.safe_load(f)
    
    global_metric_path = config['metric_path']
    collector = AppDMetricCollector(config['metric_path'])

    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(execute_script, job) for job in config['jobs']]

        for future in as_completed(futures):
            output = future.result()
            if output:  # Check if script execution was successful
                job = config['jobs'][futures.index(future)]  # Get the corresponding job
                parse_and_collect_metrics(job, output, collector, global_metric_path) # Pass config

    print(collector.get_metric_string(), flush=True)
    sys.stdout.flush()

if __name__ == "__main__":
    main()