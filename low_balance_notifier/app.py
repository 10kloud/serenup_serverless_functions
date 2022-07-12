import os

from boto_tools import DynamoDBTable, TimestreamQuerier, SNSTopicManager, CognitoIDPUserPool
from balance_image import BalanceState


def get_bracelet_owner(bracelet_id: str) -> str:
    query = (
        "SELECT DISTINCT bracelet_id, customer_id "
        f"FROM \"{os.getenv('TimestreamDatabase')}\".\"{os.getenv('TimestreamTable')}\" "
        f"WHERE bracelet_id = '{bracelet_id}' and time > ago(15m)"
    )
    querier = TimestreamQuerier()
    result = querier.exec(query)
    result_data = result[0]['data']
    if len(result_data) == 0:
        return ""
    return result_data[0]['customer_id']


def get_owner_notification_topic_name(owner_id: str) -> str:
    response = DynamoDBTable(
        table_name=os.getenv('UserTrustedContactsTable')
    ).get(key={
        'customer_id': owner_id
    })
    return response.get('sns_topic_name', None)


def lambda_handler(event: dict, context):
    if event['Records'][0]['eventName'] != "MODIFY":
        print("Ignoring event of type", event['Records'][0]['eventName'])
        return
    old_state = BalanceState.from_dynamodb_event_image(
        event['Records'][0]['dynamodb']['OldImage']
    )
    new_state = BalanceState.from_dynamodb_event_image(
        event['Records'][0]['dynamodb']['NewImage']
    )
    print(f"Received Old={old_state.balance_status} New={new_state.balance_status}")

    if old_state.balance_status == "OK" and new_state.balance_status == "FALL":
        owner_id = get_bracelet_owner(new_state.device_id)
        owner_notification_topic = get_owner_notification_topic_name(owner_id)

        if owner_notification_topic is None:
            print("Unable to query the SNS topic for", owner_id)
            return

        print("Retrieving user name from AWS Cognito")
        user_info = CognitoIDPUserPool(
            user_pool_id=os.getenv("CognitoUserPoolID")
        ).filter_user_by_sub(owner_id)['Users'][0]
        user_name = next(item for item in user_info['Attributes'] if item['Name'] == "name")['Value']
        print("User name found")

        print("Sending low battery alert to the trusted contacts of the owner of the bracelet", new_state.device_id)
        response = SNSTopicManager(owner_notification_topic).publish(
            message=f"{user_name} è caduto."
        )
        print(response)
    else:
        print("Skipping notification")
