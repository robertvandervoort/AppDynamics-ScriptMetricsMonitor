# AppDynamics-ScriptMetricsMonitor

A machine agent extension that can run any number of monitoring scripts and handle various output formats

## Getting Started

### All OS

1. Clone this repo into your machine agent's "monitors" folder.

### Linux

2. From your shell, execute the `run.sh` script. This will create a Python virtual environment, install the requirements, and if successful, execute the script, which will in turn execute three test scripts and print the output.

### Windows

2. Open a command prompt and enter the `AppDynamics-ScriptMetricsMonitor` folder inside of your machine agent's monitors folder.
3. Create a Python virtual environment:
   ```bash
   python3 -m venv venv
   ```
4. Activate the Python virtual environment:
   ```command prompt
   venv\Scripts\activate.bat
   ```
5. You should now see `(venv)` at the beginning of your command prompt. If so, continue to the next step. If not, troubleshoot.
6. Install the requirements inside the virtual environment:
   ```command prompt
   python3 -m pip install -r requirements.txt
   ```
7. Test the execution and output of the script:
   ```command prompt
   python3 ScriptMetricsMonitor.py
   ```

### All OS

At this point, if everything went well, you should see this output:

```
Custom Metrics|testmetrics|Testmetric1,value=1
Custom Metrics|testmetrics|Testmetric2,value=2
Custom Metrics|testmetrics|Testmetric3,value=11234
Custom Metrics|testmetrics|Testmetric4,value=2134432
Custom Metrics|cpu-extended|ctx_switches,value=5460
Custom Metrics|cpu-extended|interrupts,value=220045
Custom Metrics|cpu-extended|soft_interrupts,value=4294967295
Custom Metrics|cpu-extended|syscalls,value=192581
```

If you only see the "testmetrics" (first four lines), then the Python sample monitor (a perfectly useful monitor I would add) is not executing. This is likely due to a missing dependency. Make sure you installed the requirements in the prior steps. The test script requires the `psutil` library. This library will be common for Python-based monitoring scripts, so I made it a requirement in the venv.

If everything is good, edit the `config.yml` to meet your needs, removing the examples. Test the operation as above.
