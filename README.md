# AppDynamics-ScriptMetricsMonitor

A machine agent extension that can run any number of monitoring scripts and handle various output formats

## Getting Started

### All OS

1. Clone this repo into your machine agent's "monitors" folder.

### Linux

2. From your shell, execute the `run.sh` script. This will create a Python virtual environment, install the requirements, and if successful, execute the script, which will in turn execute three test scripts and print the output.

### Windows

2. Open a command prompt and enter the `AppDynamics-ScriptMetricsMonitor` folder that you cloned inside of your machine agent's monitors folder.
3. Execute the 'run.bat' script.nvironment:
   
At this point, if everything went well, you should see this output:

### Linux
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

### Windows
'''
Error processing job 'testmetrics': [WinError 193] %1 is not a valid Win32 application
Error processing job 'testmetrics': [WinError 193] %1 is not a valid Win32 application
Custom Metrics|cpu-extended|ctx_switches,value=1638559682
Custom Metrics|cpu-extended|interrupts,value=460127880
Custom Metrics|cpu-extended|soft_interrupts,value=0
Custom Metrics|cpu-extended|syscalls,value=402143940
'''

The errors here are because the first two test scripts are bash shell scripts so you can ignore those.

If you dont see the "cpu-extended" (last four lines), then the Python sample monitor (a perfectly useful monitor I would add) is not executing. This is likely due to a missing dependency. Make sure you installed the requirements in the prior steps. The test script requires the `psutil` library. This library will be common for Python-based monitoring scripts, so I made it a requirement in the venv.

If everything is good, edit the `config.yml` to meet your needs, removing the examples. Test the operation as above.

You'll need to restart the machine agent for the monitor to get picked up.
