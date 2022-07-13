from diagrams import Diagram, Cluster, Edge
from diagrams.onprem.client import User
from diagrams.aws.compute import Lambda
from diagrams.aws.network import APIGateway
from diagrams.aws.database import Dynamodb
from diagrams.aws.integration import SimpleNotificationServiceSns

with Diagram("", filename="docs/notifications"):
    user = User("User")

    api_gateway = APIGateway("API Gateway")
    create_contact = Lambda("Create Contact")
    delete_contact = Lambda("Delete Contact")
    list_contacts = Lambda("List contacts")

    contacts_topic = SimpleNotificationServiceSns("Contacts")
    trusted_contacts_topic = SimpleNotificationServiceSns("TrustedContacts")

    contacts_table = Dynamodb("ContactTopicTable")
    trusted_contacts_table = Dynamodb("TrustedContactsTable")

    battery_state = Dynamodb("BatteryState")
    balance_state = Dynamodb("BalanceState")

    low_battery_notifier = Lambda("LowBatteryNotifier")
    low_balance_notifier = Lambda("LowBalanceNotifier")

    user >> api_gateway
    api_gateway >> create_contact >> [trusted_contacts_table, contacts_table]
    api_gateway >> delete_contact >> [trusted_contacts_table, contacts_table]
    api_gateway >> list_contacts >> [trusted_contacts_table, contacts_table]

    battery_state >> Edge(label="Trigger") >> low_battery_notifier
    contacts_table << low_battery_notifier
    low_battery_notifier >> Edge(label="Send message") >> contacts_topic

    balance_state >> Edge(label="Trigger") >> low_balance_notifier
    trusted_contacts_table << low_balance_notifier
    low_balance_notifier >> Edge(label="Send message") >> trusted_contacts_topic
