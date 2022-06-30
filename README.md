## Serverless functions for SerenUp smart bracelet

### Data ingestion
Amazon Kinesis does not allow storing data coming from a Kinesis Data Stream directly,
although there's the possibility to use a lambda function that reads information from the stream and write into a Timestream database.

## API documentation
AWS API gateway allow to download current API design in OpenAPI 3.0 format:
```
aws apigateway get-export --rest-api-id <aws-api-gateway-id> --stage-name Prod --export-type oas30 openapi30.json
```
