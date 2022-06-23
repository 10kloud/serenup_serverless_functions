import base64
import json
import boto3
import os
from typing import List, Dict
from bracelet import BraceletMetric

timestream = boto3.client('timestream-write')
dynamodb = boto3.client('dynamodb')


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
            {'Name': 'region', 'Value': 'eu-west-1'},
            {'Name': 'bracelet_id', 'Value': metric.device_id},
            {'Name': 'customer_id', 'Value': metric.customer_id}
        ]
        common_attributes = dict(
            Time=str(metric.measured_at),
            TimeUnit="NANOSECONDS",
            Dimensions=dimensions,
        )
        # ID of the bracelet
        device_id = dict(
            MeasureName="device_id",
            MeasureValue=str(metric.device_id),
            MeasureValueType='VARCHAR',
        )
        # ID of the customer/user
        customer_id = dict(
            MeasureName="customer_id",
            MeasureValue=str(metric.customer_id),
            MeasureValueType='VARCHAR',
        )
        # Serendipity level of the user
        serendipity = dict(
            MeasureName="serendipity",
            MeasureValue=str(metric.serendipity),
            MeasureValueType="DOUBLE"
        )
        # Battery level of the device
        battery_level = dict(
            MeasureName="battery_level",
            MeasureValue=str(metric.battery_level),
            MeasureValueType="DOUBLE"
        )
        # When the measurement has been done
        measurement_time = dict(
            MeasureName="measured_at",
            MeasureValue=str(metric.measured_at),
            MeasureValueType="VARCHAR"
        )
        records = [
            device_id, customer_id,
            serendipity, battery_level,
            measurement_time
        ]

        timestream_write(records, common_attributes)


def timestream_write(records: List[dict], common_attributes: dict):
    try:
        timestream.write_records(
            DatabaseName=os.getenv("TIMESTREAM_DB"),
            TableName=os.getenv("TIMESTREAM_TABLE"),
            Records=records,
            CommonAttributes=common_attributes
        )
    except timestream.exceptions.RejectedRecordsException as err:
        print("[WARN] Record has been rejected")
        print("RejectedRecords: ", err)
        for rr in err.response["RejectedRecords"]:
            print("Rejected Index " + str(rr["RecordIndex"]) + ": " + rr["Reason"])
        print("Other records were written successfully. ")


def lambda_handler(event, context):
    bracelet_metrics: List[BraceletMetric] = extract_bracelet_metrics(event)
    save_bracelet_metrics(bracelet_metrics)
