from typing import List

import boto3
from botocore.exceptions import ClientError
from mypy_boto3_sns.client import SNSClient
from mypy_boto3_sns.service_resource import SNSServiceResource, Topic, Subscription
from mypy_boto3_sns.type_defs import SubscriptionTypeDef


class SNSTopicManager:
    def __init__(self, topic_name: str):
        self.__client: SNSClient = boto3.client('sns')
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

    def unsubscribe(self, subscription_arn: str):
        try:
            response = self.__client.unsubscribe(
                SubscriptionArn=subscription_arn
            )
        except ClientError as err:
            print("Unable to delete subscription", subscription_arn)
            print(
                err.response['Error']['Code'],
                err.response['Error']['Message']
            )
            raise

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

    def find_subscription_by_endpoint(self, endpoint: str) -> dict:
        for subscription in self.list_subscriptions():
            if subscription["Endpoint"] == endpoint:
                return subscription
        return {}

    def list_subscriptions(self) -> List[SubscriptionTypeDef]:
        paginator = self.__client.get_paginator('list_subscriptions_by_topic')
        response_iterator = paginator.paginate(
            TopicArn=self.__topic.arn,
        )

        for response in response_iterator:
            subscriptions = response['Subscriptions']
            for subscription in subscriptions:
                yield subscription
