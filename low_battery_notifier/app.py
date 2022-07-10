import os

from battery_status_image import BatteryStatusImage
from boto_tools.dynamo import DynamoDBTable
from boto_tools.timestream import TimestreamQuerier
from boto_tools.sns import SNSTopicManager


def get_bracelet_owner(bracelet_id: str) -> str:
    query = (
        "SELECT DISTINCT bracelet_id, customer_id "
        f"FROM \"{os.getenv('TimestreamDatabase')}\".\"{os.getenv('TimestreamTable')}\" "
        f"WHERE bracelet_id = '{bracelet_id}' and time > ago(15m)"
    )
    querier = TimestreamQuerier()
    result = querier.exec(query)

    return result[0]['data'][0]['customer_id']


def get_owner_notification_topic_name(owner_id: str) -> str:
    return DynamoDBTable(
        table_name=os.getenv('UserContactsTable')
    ).get(key={
        'customer_id': owner_id
    }).get('Item', {}).get('sns_topic_name', None)


def lambda_handler(event: dict, context):
    if event['Records'][0]['eventName'] != "MODIFY":
        print("Ignoring event of type", event['Records'][0]['eventName'])
        return

    old_image = BatteryStatusImage.from_dynamodb_event_image(
        event['Records'][0]['dynamodb']['OldImage']
    )
    new_image = BatteryStatusImage.from_dynamodb_event_image(
        event['Records'][0]['dynamodb']['NewImage']
    )
    print(f"Received Old={old_image.battery_status} New={new_image.battery_status}")

    if old_image.battery_status == "CHARGE" and new_image.battery_status == "LOW_BATTERY":
        owner_id = get_bracelet_owner(new_image.device_id)
        owner_notification_topic = get_owner_notification_topic_name(owner_id)
        print("Sending low battery alert to the owner of the bracelet", new_image.device_id)
        SNSTopicManager(owner_notification_topic).publish(
            message="Il tuo bracciale SerenUp ha la batteria scarica. Assicurati di caricarlo il prima possibile."
        )
    else:
        print("Skipping notification")
