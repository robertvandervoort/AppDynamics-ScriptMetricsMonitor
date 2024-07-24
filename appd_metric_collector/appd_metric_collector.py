class AppDMetricCollector:
    def __init__(self, base_path):
        self.base_path = base_path
        self.metrics = []

    def collect_metrics(self, metric_path, job_name, metrics_dict):
        for key, value in metrics_dict.items():
            self.metrics.append(f"name={metric_path}|{job_name}|{key}, value={value}")

    def get_metric_string(self):
        return "\n".join(self.metrics)