# Load YAML Configuration
$config = Get-Content .\config.yml | ConvertFrom-Yaml

# Initialize Metric Collector
$globalMetricPath = $config.metric_path
$collector = [AppDMetricCollector]::new($globalMetricPath)

# Process Each Job
foreach ($job in $config.jobs) {
    $scriptPath = $job.script -replace '^"|"$' # Remove quotes if present
    $scriptPath = (Resolve-Path $scriptPath).Path

    try {
        # Execute Python Scripts
        if ($scriptPath -like '*.py') {
            # Use cmd.exe for Windows compatibility
            $result = cmd.exe /c "python $scriptPath" 2>&1 # Redirect stderr to stdout

            if ($LASTEXITCODE -ne 0) {
                Write-Host "Error executing child script: $result"
            }
        } 

        # Execute Executables
        elseif ($scriptPath -like '*.exe') {
            $result = & $scriptPath -q -x | Out-String # Capture output as string
            if ($LASTEXITCODE -ne 0) {
                Write-Host "Error executing child script: $result"
            }
        } 

        # Execute Batch/Shell Scripts
        elseif ($scriptPath -like '*.cmd' -or $scriptPath -like '*.bat' -or $scriptPath -like '*.sh') {
            $result = & $scriptPath 2>&1
            if ($LASTEXITCODE -ne 0) {
                Write-Host "Error executing child script: $result"
            }
        } 

        # Execute Other Scripts/Commands
        else {
            $result = & $scriptPath 2>&1
            if ($LASTEXITCODE -ne 0) {
                Write-Host "Error executing child script: $result"
            }
        }

        # Parse and Collect Metrics
        if ($result) { # Check if script execution was successful
            $metricPath = $job.metric_path
            if (-not $metricPath) { $metricPath = $globalMetricPath }

            $metrics = @{}
            
            #Write-Host "Raw Result: $result"
            
            switch ($job.output_format) {
                'json' {

                    $parsedJson = $result | ConvertFrom-Json 

                    # Iterate over the properties in the parsed JSON
                    foreach ($key in $parsedJson.psobject.Properties.Name) {
                        $metrics[$key] = $parsedJson.$key
                    }
                }
                'xml' {
                    # Basic XML parsing; may need adjustment for complex XML
                    $xml = [xml]$result
                    $metrics = $xml.SelectNodes("//*") | ForEach-Object {
                        @{ $_.Name = $_.InnerText }
                    }
                }
                default { # keyvalue or key=value
                    $result -split "`n" | ForEach-Object {
                        if ($_ -match '^(.*?)=(.*)$') {
                            $metrics[$Matches[1].Trim()] = $Matches[2].Trim()
                        } elseif ($_ -match '^(.*?)\s+(.*)$') {
                            $metrics[$Matches[1].Trim()] = $Matches[2].Trim()
                        }
                    }
                }
            }

            # Rename Metrics if Needed
            if ($job.ContainsKey('metrics')) {
                foreach ($mapping in $job.metrics) {
                    if ($metrics.ContainsKey($mapping.original_name)) {
                        $metrics[$mapping.metric_name] = $metrics[$mapping.original_name]
                        $metrics.Remove($mapping.original_name)
                    }
                }
            }

            # Collect Metrics
            $collector.CollectMetrics($metricPath, $job.name, $metrics)
        }

    } catch {
        Write-Host "Error processing job '$($job.name)': $_"
    }
}

# Output Metric String
Write-Host $collector.GetMetricString()

# Define AppDMetricCollector Class
class AppDMetricCollector {
    [string]$basePath
    [System.Collections.Generic.List[string]]$metrics

    AppDMetricCollector([string]$basePath) {
        $this.basePath = $basePath
        $this.metrics = [System.Collections.Generic.List[string]]::new()
    }

    [void]CollectMetrics([string]$metricPath, [string]$jobName, [hashtable]$metricsDict) {
        foreach ($key in $metricsDict.Keys) {
            $this.metrics.Add("name=$metricPath|$jobName|$key, value=$($metricsDict[$key])")
        }
    }

    [string]GetMetricString() {
        return $this.metrics -join "`n"
    }
}