import json
import os

import boto3

from responses import bracelet_not_found
from timestream_querier import TimestreamQuerier

timestream = boto3.client('timestream-query')


def build_query(bracelet_id: str, measure_name: str, time_from: str = "1h") -> str:
    if measure_name == "":
        return f"""
        select *
        from "{os.getenv("TIMESTREAM_DB")}"."{os.getenv("TIMESTREAM_TABLE")}"
        where bracelet_id='{bracelet_id}' and time > ago({time_from})
        """
    # Specify query for a certain measure since client is not able to know its type
    elif measure_name == "serendipity":
        return f"""
        select time, measure_name, measure_value::double as measure_value
        from "{os.getenv("TIMESTREAM_DB")}"."{os.getenv("TIMESTREAM_TABLE")}"
        where bracelet_id='{bracelet_id}' and measure_name='{measure_name}' and time > ago({time_from})
        """


def lambda_handler(event: dict, context):
    bracelet_id = event.get("pathParameters", {}).get("bracelet_id", None)
    if bracelet_id is None:
        return bracelet_not_found(bracelet_id)

    query_string_parameters = event.get("queryStringParameters", dict())
    if query_string_parameters is None:
        query_string_parameters = dict()

    metric = query_string_parameters.get("metric", "")
    time_from = query_string_parameters.get("from", "1d")

    query = build_query(bracelet_id, metric, time_from)
    querier = TimestreamQuerier(timestream)
    result = querier.exec(query)

    return dict(
        statusCode=200,
        body=json.dumps(result)
    )
