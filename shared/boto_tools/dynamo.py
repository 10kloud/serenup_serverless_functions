from typing import Union

import boto3
from botocore.exceptions import ClientError
from mypy_boto3_dynamodb.service_resource import DynamoDBServiceResource
from mypy_boto3_dynamodb.type_defs import PutItemOutputTableTypeDef


class DynamoDBTable:
    def __init__(self, table_name: str):
        self.__resource: DynamoDBServiceResource = boto3.resource('dynamodb')
        self.__table = self.__resource.Table(table_name)

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
            return response['Item']

