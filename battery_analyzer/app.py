import os
from typing import List, Dict, Generator

from models import BraceletMetric
from boto_tools import DynamoDBTable


def metrics_from_stream(records: List[Dict[str, Dict]]) -> Generator[BraceletMetric, None, None]:
    for record in records:
        yield BraceletMetric.from_kinesis_record(record)


def update_status(device_id: str, metric_name: str, metric_value):
    status_table = DynamoDBTable(
        table_name=os.getenv("BatteryAnalyticsDynamoTable")
    )
    attributes = status_table.update(
        key={'device_id': device_id},
        update_expression=f"SET {metric_name}=:b",
        condition_expression=f"{metric_name} <> :b",
        expression_attribute_values={':b': metric_value},
    )
    return attributes


def lambda_handler(event, context):
    for metric in metrics_from_stream(event.get('Records', [])):
        res = update_status(
            device_id=metric.device_id,
            metric_name="battery",
            metric_value=metric.battery_status
        )
        print(res)

    print("Execution completed. All statuses updated")
