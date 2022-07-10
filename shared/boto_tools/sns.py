import boto3
from botocore.exceptions import ClientError

from mypy_boto3_sns.service_resource import SNSServiceResource, Topic, Subscription


class SNSTopicManager:
    def __init__(self, topic_name: str):
        self.__resource: SNSServiceResource = boto3.resource('sns')
        print(f"Gathering or creating topic {topic_name}")
        self.__topic: Topic = self.__resource.create_topic(
            Name=topic_name
        )
        print(f"Topic {topic_name} gathered successfully")

    def subscribe(self, protocol: str, endpoint: str) -> Subscription:
        print("Subscribing contact to topic")
        try:
            subscription: Subscription = self.__topic.subscribe(
                Endpoint=endpoint,
                Protocol=protocol,
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

    def publish(self, message: str):
        try:
            response = self.__topic.publish(
                Message=message,
            )
            print(f"Published message {response['MessageId']}")
        except ClientError as err:
            print(
                "Error while sending message",
                err.response['Error']['Code'],
                err.response['Error']['Message']
            )
            raise
        else:
            return response['MessageId']
