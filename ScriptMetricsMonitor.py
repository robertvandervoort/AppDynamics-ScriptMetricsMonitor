#! python

import os
import sys
import contextlib
import xml.etree.ElementTree as ET
import subprocess
import json
import yaml
from appd_metric_collector.appd_metric_collector import AppDMetricCollector

def main():
    """Main program code"""
    #1. Read Config"""
    with open("config.yml", 'r') as f:
        config = yaml.safe_load(f)

    # 2. Initialize Metric Collector (Abstraction for AppD metric formatting)
    collector = AppDMetricCollector(config['metric_path'])

    # 3. Iterate Over Jobs
    for job in config['jobs']:
        try:
            # 3.1 Execute Script
            script_path = repr(job['script'])[1:-1]  # Convert to raw string
            script_path = os.path.normpath(script_path)

            if script_path.endswith('.py'):
                if sys.version_info >= (3, 7):  # Python 3.7+
                    result = subprocess.run(['python', script_path], capture_output=True, text=True, bufsize=0, check=False)
                else:
                    with contextlib.closing(subprocess.Popen(['python', script_path], stdout=subprocess.PIPE, bufsize=0)) as proc:
                        result = proc.stdout.read().decode()
            
            elif script_path.endswith('.exe'): #for .exe progs
                try:
                    result = subprocess.check_output([script_path, "-q", "-x"], universal_newlines=True)
                except subprocess.CalledProcessError as e:
                    print("Error executing command:", e)
                    result = None
            
            elif script_path.endswith(('.cmd', '.bat')):  # Handle .cmd and .bat files
                result = subprocess.run([script_path], shell=True, capture_output=True, text=True, bufsize=0, check=False)

            else:
                if sys.version_info >= (3, 7):  # Python 3.7+
                    result = subprocess.run([script_path], capture_output=True, text=True, bufsize=0, check=False)
                else:
                    with contextlib.closing(subprocess.Popen([script_path], stdout=subprocess.PIPE, bufsize=0)) as proc:
                        result = proc.stdout.read().decode()

            # 3.2 Parse Output
            metrics = {}
            if job['output_format'] == 'json':
                metrics = json.loads(result.stdout)
            elif job['output_format'] == 'xml':
                root = ET.fromstring(result.stdout)
                metrics = {elem.tag: elem.text for elem in root.iter()}
            else:  # keyvalue or key=value
                for line in result.stdout.splitlines():
                    key, value = line.split('=', 1) if '=' in line else line.split(None, 1)
                    metrics[key.strip()] = value.strip()

            # 3.3 Rename Metrics (Optional)
            if 'metrics' in job:
                for mapping in job['metrics']:
                    if mapping['original_name'] in metrics:
                        metrics[mapping['metric_name']] = metrics.pop(mapping['original_name'])

            # 3.4 Collect Metrics
            metric_path = job.get('metric_path', config.get('metric_path', "Custom Metrics|ScriptMetrics"))  # Fallback to global
            collector.collect_metrics(metric_path, job['name'], metrics)

        except Exception as e:
            print(f"Error processing job '{job['name']}': {e}")

    # 4. Print Metrics to STDOUT (AppDynamics will pick them up)
    print(collector.get_metric_string())

if __name__ == "__main__":
    main()