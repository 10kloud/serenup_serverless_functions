import boto3
from botocore.exceptions import ClientError

from metrics_analyzer import MetricAnalysisResult


class AnalyticsResultWriter:
    def __init__(self, table_name: str):
        self.table = boto3.resource('dynamodb').Table(table_name)

    def update_result(self, result: MetricAnalysisResult):
        try:
            response = self.table.update_item(
                Key={
                    'device_id': result.device_id
                },
                UpdateExpression="SET battery=:b",
                ExpressionAttributeValues={
                    ':b': result.battery
                },
                ReturnValues="UPDATED_NEW"
            )
        except ClientError as err:
            print((
                f"Could not update metric analysis result for device_id={result.device_id}:"
                f"{err.response['Error']['Code']} - {err.response['Error']['Message']}"
            ))
        else:
            return response['Attributes']
