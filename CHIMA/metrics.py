class Metrics:
    def __init__(self, latency, jitter):
        self.latency = latency
        self.jitter = jitter

collected_metrics = {}