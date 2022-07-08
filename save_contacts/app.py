import json
import os

from botocore.exceptions import ClientError

from contact import Contact
from responses import Ok, BadRequest
from boto_tools.sns import SNSTopicManager
from boto_tools.dynamo import DynamoDBTable

contacts_category_mapping = {
    "trusted_contact": os.getenv('UserTrustedContactsTable'),
    "notifications": os.getenv('UserContactsTable')
}


def lambda_handler(event: dict, context):
    customer_id = event.get("pathParameters", {}).get("customer_id", None)
    print(f"Adding contact to {customer_id}")

    contact = Contact.from_json(json.loads(event['body']))
    topic = f"{customer_id}_{contact.category}"
    table = contacts_category_mapping[contact.category]

    try:
        sns_topic = SNSTopicManager(topic)
        subscription = sns_topic.subscribe(contact.protocol, contact.endpoint)
        contacts = DynamoDBTable(table)
        contacts.put(
            item=dict(
                customer_id=customer_id,
                sns_subscription_arn=subscription['SubscriptionArn']
            )
        )
    except ClientError as err:
        return BadRequest(body=dict(
            errorCode=err.response['Error']['Code'],
            errorMessage=err.response['Error']['Message']
        ))

    return Ok(body=dict(
        message="User subscribed successfully"
    ))
