import boto3
from botocore.exceptions import ClientError

from mypy_boto3_sns.client import SNSClient
from mypy_boto3_sns.type_defs import CreateTopicResponseTypeDef, SubscribeResponseTypeDef


class SNSTopicManager:
    def __init__(self, topic_name: str):
        self.__client: SNSClient = boto3.client('sns')
        print(f"Gathering or creating topic {topic_name}")
        self.__topic: CreateTopicResponseTypeDef = self.__client.create_topic(
            Name=topic_name
        )
        print(f"Topic {topic_name} gathered successfully")

    def subscribe(self, protocol: str, endpoint: str) -> SubscribeResponseTypeDef:
        print("Subscribing contact to topic")
        try:
            subscription = self.__client.subscribe(
                TopicArn=self.__topic["TopicArn"],
                Protocol=protocol,
                Endpoint=endpoint,
                ReturnSubscriptionArn=True
            )
        except ClientError as err:
            print(
                "Error while subscribing this endpoint",
                err.response['Error']['Code'],
                err.response['Error']['Message']
            )
            raise
        else:
            print("Contact subscribed successfully")
            return subscription

