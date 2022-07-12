import json
import os

from botocore.exceptions import ClientError

from boto_tools import DynamoDBTable, SNSTopicManager
from responses import BadRequest, ResourceNotFound, Gone

contacts_category_mapping = {
    "trusted_contact": os.getenv('UserTrustedContactsTable'),
    "notifications": os.getenv('UserContactsTable')
}


def lambda_handler(event: dict, context):
    customer_id = event.get("pathParameters", {}).get("customer_id", None)
    print(f"Getting contacts for {customer_id}")

    body = json.loads(event['body'])
    endpoint = body.get("endpoint", None)
    category = body.get("category", None)
    if endpoint is None or category is None:
        return BadRequest(body="Error while parsing body. Missing endpoint or category")

    table = contacts_category_mapping[category]

    try:
        # Get topic name
        contacts = DynamoDBTable(table)
        topic_name = contacts.get(key={
            "customer_id": customer_id
        }).get("sns_topic_name", None)

        if topic_name is None:
            return ResourceNotFound(body="Unable to find contact information about the given customer_id")

        # Get all subscribers of that topic
        topic = SNSTopicManager(topic_name)
        subscription = topic.find_subscription_by_endpoint(endpoint)
        if not subscription.get("SubscriptionArn", False):
            return ResourceNotFound(body=dict(
                errorCode="Subscription not found",
                errorMessage="Unable to find a subscription for the given endpoint or it's still in pending state"
            ))
        topic.unsubscribe(subscription["SubscriptionArn"])
    except ClientError as err:
        return BadRequest(body=dict(
            errorCode=err.response['Error']['Code'],
            errorMessage=err.response['Error']['Message']
        ))

    return Gone(body=dict(
        message="Subscription deleted successfully"
    ))
