import json
import os

from botocore.exceptions import ClientError

from contact import Contact
from responses import Ok, BadRequest
from boto_tools import SNSTopicManager, DynamoDBTable

contacts_category_mapping = {
    "trusted_contact": os.getenv('UserTrustedContactsTable'),
    "notifications": os.getenv('UserContactsTable')
}


def lambda_handler(event: dict, context):
    topic_prefix = os.getenv('NotificationTopicPrefix')
    customer_id = event.get("pathParameters", {}).get("customer_id", None)
    print(f"Adding contact to {customer_id}")

    contact = Contact.from_json(json.loads(event['body']))
    topic = f"{topic_prefix}_{customer_id}_{contact.category}"
    table = contacts_category_mapping[contact.category]

    try:
        # Create topic
        SNSTopicManager(topic).subscribe(
            protocol=contact.protocol,
            endpoint=contact.endpoint
        )

        # Save topic info
        contacts = DynamoDBTable(table)
        contacts.put(
            item=dict(
                customer_id=customer_id,
                sns_topic_name=topic
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
