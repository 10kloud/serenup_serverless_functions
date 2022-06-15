## Serverless functions for SerenUp smart bracelet

### Data ingestion
Amazon Kinesis does not allow storing data coming from a Kinesis Data Stream directly,
although there's the possibility to use a lambda function that reads information from the stream and write into a Timestream database.