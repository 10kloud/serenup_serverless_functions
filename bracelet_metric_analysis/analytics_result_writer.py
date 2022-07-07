import boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key, Attr

from metrics_analyzer import MetricAnalysisResult


class AnalyticsResultWriter:
    def __init__(self, metric: str, table_name: str):
        self._metric = metric
        self.table = boto3.resource('dynamodb').Table(table_name)

    def update_battery(self, result: MetricAnalysisResult):
        try:
            response = self.table.update_item(
                Key={
                    'device_id': result.device_id
                },
                UpdateExpression=f"SET {self._metric}=:b",
                ExpressionAttributeValues={
                    ':b': result.battery
                },
                ReturnValues="UPDATED_NEW",
                ConditionExpression=Attr(self._metric).ne(result.battery)
            )
        except ClientError as err:
            if err.response['Error']['Code'] == "ConditionalCheckFailedException":
                print("Value has not been updated since the new value is equal to the old one")
            else:
                print((
                    f"Could not update {self._metric} for device_id={result.device_id}: "
                    f"{err.response['Error']['Code']} - {err.response['Error']['Message']}"
                ))
        else:
            return response['Attributes']
