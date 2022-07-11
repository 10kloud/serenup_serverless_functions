import os

from botocore.exceptions import ClientError

from boto_tools.dynamo import DynamoDBTable
from boto_tools.sns import SNSTopicManager
from responses import Ok, BadRequest

contacts_category_mapping = {
    "trusted_contact": os.getenv('UserTrustedContactsTable'),
    "notifications": os.getenv('UserContactsTable')
}


def lambda_handler(event: dict, context):
    customer_id = event.get("pathParameters", {}).get("customer_id", None)
    print(f"Getting contacts for {customer_id}")

    # Select contact category
    # If nothing is specified, then "notifications" will be used
    contact_category = event \
        .get("queryStringParameters", {}) \
        .get("category", "notifications")
    table = contacts_category_mapping[contact_category]

    try:
        # Get topic name
        contacts = DynamoDBTable(table)
        topic_name = contacts.get(key={
            "customer_id": customer_id
        }).get("sns_topic_name", None)

        if topic_name is None:
            return Ok(body=[])

        # Get all subscribers of that topic
        topic = SNSTopicManager(topic_name)
        subscriptions = list()

        for sub in topic.list_subscriptions():
            # Subscription Arn is set to an AWS ARN only if the user has confirmed the subscription
            sub_status = "Confirmed" if sub['SubscriptionArn'].startswith("arn:aws:sns:") else "Pending confirmation"
            subscriptions.append(
                dict(
                    protocol=sub['Protocol'],
                    endpoint=sub['Endpoint'],
                    status=sub_status
                )
            )
    except ClientError as err:
        return BadRequest(body=dict(
            errorCode=err.response['Error']['Code'],
            errorMessage=err.response['Error']['Message']
        ))

    return Ok(body=subscriptions)
