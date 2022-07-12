from typing import Dict

import boto3
from botocore.exceptions import ClientError
from mypy_boto3_dynamodb.service_resource import DynamoDBServiceResource
from mypy_boto3_dynamodb.type_defs import PutItemOutputTableTypeDef


class DynamoDBTable:
    def __init__(self, table_name: str):
        self.__resource: DynamoDBServiceResource = boto3.resource('dynamodb')
        self.__table = self.__resource.Table(table_name)

    def update(self,
               key: Dict[str, str],
               update_expression: str,
               expression_attribute_values: Dict,
               condition_expression: str,
               return_values: str = "UPDATED_NEW"
               ):
        try:
            response = self.__table.update_item(
                Key=key,
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_attribute_values,
                ConditionExpression=condition_expression,
                ReturnValues=return_values
            )
        except ClientError as err:
            if err.response['Error']['Code'] == "ConditionalCheckFailedException":
                print("Value has not been updated since the new value is equal to the old one")
            else:
                print((
                    f"Could not update item with key={key}"
                    f"{err.response['Error']['Code']} - {err.response['Error']['Message']}"
                ))
                raise
        else:
            return response['Attributes']

    def put(self, item: dict) -> PutItemOutputTableTypeDef:
        try:
            response = self.__table.put_item(
                Item=item
            )
            return response
        except ClientError as err:
            print(
                "Cannot put record in dyanamodb table",
                err.response['Error']['Code'],
                err.response['Error']['Message']
            )
            raise

    def get(self, key: dict):
        try:
            response = self.__table.get_item(Key=key)
        except ClientError as err:
            print(
                "Cannot read record from table",
                err.response['Error']['Code'],
                err.response['Error']['Message']
            )
            raise
        else:
            return response.get('Item', {})
