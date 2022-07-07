import base64
import json
import os
from typing import List, Dict
from metrics_analyzer import MetricAnalysisResult, MetricsAnalyzer
from analytics_result_writer import AnalyticsResultWriter

import boto3

from bracelet import BraceletMetric


def extract_bracelet_metrics(event: Dict[str, List]) -> List[BraceletMetric]:
    records: List[Dict[str, Dict]] = event.get('Records', [])
    return [
        BraceletMetric.from_dict(
            json.loads(
                base64.b64decode(
                    record['kinesis']['data']
                )
            )
        )
        for record in records
    ]


def lambda_handler(event, context):
    bracelet_metrics: List[BraceletMetric] = extract_bracelet_metrics(event)
    print("Parsed bracelet metrics")
    print("Analyzing bracelet metrics...")
    analysis_results: List[MetricAnalysisResult] = [
        MetricsAnalyzer.analyze(m)
        for m in bracelet_metrics
    ]
    print("Analyzed bracelet metrics")
    print("Saving results in DynamoDB")
    writer = AnalyticsResultWriter(os.getenv("BatteryAnalyticsDynamoTable"))
    for ar in analysis_results:
        print(writer.update_result(ar))
    print("Saved results in DynamoDB")
