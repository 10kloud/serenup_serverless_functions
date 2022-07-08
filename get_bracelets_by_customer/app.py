import json
import os

import boto3

from responses import Ok
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
    print(f"Requested bracelets owned by {customer_id}")

    query = build_query(customer_id)
    tsquery = TimestreamQuery(timestream)
    print("Start querying the database")
    result = tsquery.run_query(query)
    print("Got query result")

    return Ok(body=result[0])
