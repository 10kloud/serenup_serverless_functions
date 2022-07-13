from diagrams import Diagram
from diagrams.onprem.client import User
from diagrams.aws.analytics import KinesisDataStreams
from diagrams.aws.compute import Lambda
from diagrams.aws.database import Timestream

with Diagram("", filename="docs/ingester"):
    User("SerenUp Customer") \
        >> KinesisDataStreams("BraceletMetricIngester") \
        >> Lambda("KinesisToTimestream") \
        >> Timestream("BraceletMetrics")
