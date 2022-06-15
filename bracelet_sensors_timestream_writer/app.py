import base64
import json
import boto3
import os

timestream = boto3.client('timestream-write')


def record_to_bracelet_data(event):
    return [
        json.loads(base64.b64decode(record['kinesis']['data']))
        for record in event.get('Records', [])
    ]


def write_to_timestream(data):
    for r in data:
        dimensions = [
            {'Name': 'region', 'Value': 'eu-west-1'},
            {'Name': 'device_id', 'Value': r.get("device_id")},
            {'Name': 'customer_id', 'Value': r.get("customer_id")}
        ]
        common_attributes = dict(
            Time=str(r["measured_at"]),
            TimeUnit="NANOSECONDS",
            Dimensions=dimensions,
        )
        # ID of the bracelet
        device_id = dict(
            MeasureName="device_id",
            MeasureValue=r.get("device_id"),
            MeasureValueType='VARCHAR',
        )
        # ID of the customer/user
        customer_id = dict(
            MeasureName="customer_id",
            MeasureValue=r.get("customer_id"),
            MeasureValueType='VARCHAR',
        )
        # Serendipity level of the user
        serendipity = dict(
            MeasureName="serendipity",
            MeasureValue=str(r.get("serendipity")),
            MeasureValueType="DOUBLE"
        )
        # When the measurement has been done
        measure_time = dict(
            MeasureName="measured_at",
            MeasureValue=str(r.get("measured_at")),
            MeasureValueType="VARCHAR"
        )

        records = [device_id, customer_id, serendipity, measure_time]

        try:
            timestream.write_records(
                DatabaseName=os.getenv("TIMESTREAM_DB"),
                TableName=os.getenv("TABLE_NAME"),
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
    bracelet_sensor_data = record_to_bracelet_data(event)
    write_to_timestream(bracelet_sensor_data)
