from diagrams import Diagram
from diagrams.onprem.client import User
from diagrams.aws.analytics import KinesisDataStreams, KinesisDataFirehose
from diagrams.aws.storage import S3
from diagrams.aws.database import Dynamodb
from diagrams.aws.compute import Lambda

with Diagram("", filename="docs/analysis"):
    user = User("SerenUp Customer")
    data_stream = KinesisDataStreams("BraceletMetricIngester")
    firehose = KinesisDataFirehose("DataWarehousePipeline")
    data_warehouse = S3("DataWarehouse")

    user >> data_stream >> firehose >> data_warehouse

    battery_analyzer = Lambda("BatteryAnalyzer")
    battery_state = Dynamodb("BatteryState")
    data_stream >> battery_analyzer >> battery_state

    balance_analyzer = Lambda("BalanceAnalyzer")
    balance_state = Dynamodb("BalanceState")
    data_stream >> balance_analyzer >> balance_state
