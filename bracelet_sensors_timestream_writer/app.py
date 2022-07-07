import base64
import json
import os
from typing import List, Dict

import boto3

from bracelet import BraceletMetric

timestream = boto3.client('timestream-write')


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


def save_bracelet_metrics(metrics: List[BraceletMetric]):
    for metric in metrics:
        dimensions = [
            {'Name': 'bracelet_id', 'Value': metric.device_id},
            {'Name': 'customer_id', 'Value': metric.customer_id}
        ]
        common_attributes = dict(
            Time=str(metric.measured_at),
            TimeUnit="NANOSECONDS",
            Dimensions=dimensions,
        )
        # Serendipity level of the user
        serendipity = dict(
            MeasureName="serendipity",
            MeasureValue=str(round(metric.serendipity, 2)),
            MeasureValueType="DOUBLE"
        )
        # Battery level of the device
        battery_level = dict(
            MeasureName="battery_level",
            MeasureValue=str(round(metric.battery_level, 2)),
            MeasureValueType="DOUBLE"
        )
        # User balance
        balance = dict(
            MeasureName="balance",
            MeasureValue=str(round(metric.balance, 2)),
            MeasureValueType="DOUBLE"
        )
        records = [
            serendipity, battery_level, balance
        ]

        timestream_write(records, common_attributes)


def timestream_write(records: List[dict], common_attributes: dict):
    try:
        result = timestream.write_records(
            DatabaseName=os.getenv("TIMESTREAM_DB"),
            TableName=os.getenv("TIMESTREAM_TABLE"),
            Records=records,
            CommonAttributes=common_attributes
        )
        print("WriteRecords Status: [%s]" % result['ResponseMetadata']['HTTPStatusCode'])
    except timestream.exceptions.RejectedRecordsException as err:
        print("[WARN] Record has been rejected")
        print("RejectedRecords: ", err)
        for rr in err.response["RejectedRecords"]:
            print("Rejected Index " + str(rr["RecordIndex"]) + ": " + rr["Reason"])
        print("Other records were written successfully. ")


def lambda_handler(event, context):
    bracelet_metrics: List[BraceletMetric] = extract_bracelet_metrics(event)
    save_bracelet_metrics(bracelet_metrics)
