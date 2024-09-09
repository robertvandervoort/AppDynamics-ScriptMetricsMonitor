# AppDynamics-ScriptMetricsMonitor

A machine agent extension that can run any number of monitoring scripts simultaneously, handling various output formats and piping them up to AppDynamics.

## Getting Started

### All OS

##Requirements
* Python >= 3.7. I have tried to include compatibility for earlier versions (sub 3.7 but still 3.x) but haven't tested extensively.
* Ability to start / stop machine agents.
* Permissions to change folder permissions if needed

##Installation
1. Shut down the machine agent on the server you're installing this on. If you can't shut the machine agent down for a few minutes (I get it! We're monitoring stuff!) then clone this script into another folder. Where it sits for testing isn't that important. Once you're happy with it, you can move it into the machine agent's monitors folder and restart the machine agent then.
3. Clone this repo into your machine agent's "monitors" folder. Or elsewhere if you didn't shut the agent down as mentioned before.

### Linux

3. Ensure that the user your machine agent runs under has full accesss to the directory tree that you cloned this project into.
4. Enter the scripts subfolder and do a chmod +x on the .sh files within if you want to test this script using them.
5. Edit the config.yml in the root folder of this script and uncomment the jobs you'd like to use as tests. I recommend uncommenting all just to make sure everything is working as designed.
6. From your shell, execute the `run.sh` script. This will create a Python virtual environment, install the requirements, and if successful, execute the script, which will in turn execute three test scripts and print the output.

### Windows

3. Open a command prompt and enter the `AppDynamics-ScriptMetricsMonitor` folder that you cloned inside of your machine agent's monitors folder.
4. If you want to use the test scripts in the scripts folder you'll need to change the config.yml. Uncomment the jobs and change the path and script name. They are set to .sh by default so switch those to .cmd back or forward slashes do not matter.
5. Execute the `run.cmd` file.
   
At this point, if everything went well and you edited the config.yml to run all the tests, you should see this output:

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

If you didn't change the extensions on the first two jobs in the config.yml for Windows users, you'll see this:

### Windows
```
Error processing job 'testmetrics': [WinError 193] %1 is not a valid Win32 application
Error processing job 'testmetrics': [WinError 193] %1 is not a valid Win32 application
Custom Metrics|cpu-extended|ctx_switches,value=1638559682
Custom Metrics|cpu-extended|interrupts,value=460127880
Custom Metrics|cpu-extended|soft_interrupts,value=0
Custom Metrics|cpu-extended|syscalls,value=402143940
```

The errors here are because the first two test scripts setup in the config.yml are bash shell scripts. If you want to test, I have included Windows .cmd equivalents, just modify the config.yml as stated above.

If you dont see the "cpu-extended" (last four lines), then the Python sample monitor is not executing. This is likely due to a missing dependency or access issue. Make sure you installed the requirements in the prior steps. Since the run script creates a virtual environment, you generally should not run it as root in Linux.The test script requires the `psutil` library. This library will be common for Python-based monitoring scripts, so I made it a requirement in the venv.

If everything is good, edit the `config.yml` to meet your needs, removing the examples. Test the operation as above using the `run.sh` or `run.cmd` scripts. Do this before restarting your machine agent or the agent will create the test metrics under the hosts Custom MEtrics path which we don't want.

Once you're satisfied everything is as you want it to look output and path wise, you'll need to start the machine agent for the monitor to get picked up.

###Configuration

The config.yml file adopts a format similar to Prometheus job configurations in several ways. Let's break it down.

```
# Optional: Global default metric path (used if not specified per job)
metric_path: "Custom Metrics" 

jobs:
  - name: "testmetrics"
    script: "scripts/testmetrics.sh"
    output_format: "keyvalue" # Options: json, xml, keyvalue, key=value
    metric_path: "Custom Metrics"   # Job-specific metric path
    metrics: # Optional metric renaming
      - original_name: "my_key"
        metric_name: "CustomMetricName"
```

`metric_path` in the very top level of the yaml: This is used if you don't specify the path in the job. This follows AppD's standard and just places any custommetric underneath the entity (server) in the Custom Metrics path in the metric browser.

`jobs:` contains all the jobs! Each job is defined below.

`name:` This field defines the job name and will serve as the next path segment for the metric. In the example given that would be `Custom Metrics | testmetrics` An important note here is that job names DO NOT HAVE TO BE UNIQUE. Since the purpose it serves is to create the path segment, you can use the same job name for several jobs. This keeps those metrics together in the same segment. There are lots of reason you'd want to do this and I do so in the exmaples.

`script:` The path to the script you want to execute. In the example I'm using a relative path because the scripts sit in the monitoring scripts folder in a folder called scripts. You can put absolute paths here or move your mointoring scripts into the scripts folder. Whatever works. Generally I recommend keeping them in another location in the case where you might upgrade the machine agent and the folder gets wiped our, that would be unfortunate!

`output_format:` Options are `json`, `xml`, `keyvalue`, `key=value`
   json - we expect a single level of json currently. The output should be similar to the sample python monitoring script `cpu-extended.py`
   
   ```   
      {
          "ctx_switches": 3529,
          "interrupts": 176456,
          "soft_interrupts": 2686068693,
          "syscalls": 178295
      }
   ```

`metric_path:` Here it is again! This will override the global default above and is generally how I'd recommend you proceed. This sets the base path of your metrics. In my example above, these are really CPU metrics around context switches and if I wanted to see those in the CPU metrics I would set the path to `Hardware Resources` and the job name to `CPU`.

`metrics:` This section does metric renaming. This is a convenience factor for some and need for others. If you wrote your monitoring scripts of course you can go change the metric names in your code. If someone else wrote them or you have no access to change them, this comes in super handy.
   `- original_name: "my_key"` The metric name in the output of the script in question to match on.
     `metric_name: "CustomMetricName"` The new name for the metric that we matched above.

And that's it. Just add another section like this for each script you want this monitor to run. 

## Notes
I have included two python scripts in this repo. one is `AsyncScriptMetricsMonitor.py` which runs all the jobs at once. This ensures consistency in timestamping of the data since all run at the same time. This is the latest iteration of the code and the one that the monitor.xml is configured to use. I have also included `ScriptMetricsMonitor.py` which is the first iteration of the script. It runs jobs consecutively. There may be reasons you wish to do this. Perhaps a script you have requires another script to have run beforehand in order for some data to be available. That's ok! You can hava a jab that gets run and has no output for the sake of metrics. If you need scripts to run in a specific order, use this one.
