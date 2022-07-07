from dataclasses import dataclass
from typing import Dict

from bracelet import BraceletMetric


@dataclass
class MetricAnalysisResult:
    device_id: str
    battery: str


class MetricsAnalyzer:
    thresholds: Dict[str, float] = dict(
        battery=20.0
    )

    @staticmethod
    def analyze(metric: BraceletMetric):
        return MetricAnalysisResult(
            device_id=metric.device_id,
            battery="CHARGE" if metric.battery_level > 20 else "LOW_BATTERY"
        )
