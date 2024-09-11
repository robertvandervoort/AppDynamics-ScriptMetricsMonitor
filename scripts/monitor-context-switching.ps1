# Get the specific counters using Get-Counter
$counters = Get-Counter "\Processor(_Total)\Interrupts/sec", "\System\Context Switches/sec", "\System\System Calls/sec"

# Extract the relevant counter values
$interrupts = $counters.CounterSamples.CookedValue[0]
$ctxSwitches = $counters.CounterSamples.CookedValue[1]
$syscalls = $counters.CounterSamples.CookedValue[2]

# Create the metrics object
$metrics = @{
    ctx_switches = $ctxSwitches
    interrupts = $interrupts
    syscalls = $syscalls
}

# Convert to JSON and return
return $metrics | ConvertTo-Json -Depth 4
