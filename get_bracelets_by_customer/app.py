import boto3
import json
import os
from tsquery import TimestreamQuery

timestream = boto3.client('timestream-query')


def build_query(customer_id: str) -> str:
    return f"""
select distinct bracelet_id, customer_id
from "{os.getenv("TIMESTREAM_DB")}"."{os.getenv("TIMESTREAM_TABLE")}"
where customer_id='{customer_id}'
"""


def lambda_handler(event: dict, context):
    customer_id = event.get("pathParameters", {}).get("customer_id", None)

    if customer_id is None:
        return dict(
            statusCode=404,
            headers={
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET"
            },
            body=json.dumps(dict(
                message="Customer not found"
            ))
        )

    print(f"Requested bracelets owned by {customer_id}")

    query = build_query(customer_id)

    tsquery = TimestreamQuery(timestream)
    result = tsquery.run_query(query)

    return dict(
        statusCode=200,
        headers={
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET"
        },
        body=json.dumps(result)
    )

