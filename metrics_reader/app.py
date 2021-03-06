import os

import boto3

from responses import Ok
from timestream_querier import TimestreamQuerier

timestream = boto3.client('timestream-query')

measures_typed_as_double = [
    "serendipity", "battery_level", "balance"
]


def query_fields(measure_name: str):
    if measure_name == "":
        return "*"
    elif measure_name in measures_typed_as_double:
        return "time, measure_name, measure_value::double as measure_value"
    return ""


def build_query(database_name: str, table_name: str, bracelet_id: str, measure_name: str = "",
                time_from: str = "1h") -> str:
    """
    Prepare query for timestream table

    :param database_name: Name of the timestream DB
    :param table_name: Name of the timestream table
    :param bracelet_id: Query for metrics belonging to this bracelet
    :param measure_name: Name of the measure to query
    :param time_from: TODO
    :return: Query string
    """
    table = f'"{database_name}"."{table_name}"'
    fields = query_fields(measure_name)

    where = f"bracelet_id='{bracelet_id}' AND time>ago({time_from}) "
    where += f"AND measure_name='{measure_name}'" if fields != "*" else ""

    query = (
        f"SELECT {fields} "
        f"FROM {table} "
        f"WHERE {where}"
    )
    return query


def lambda_handler(event: dict, context):
    bracelet_id = event.get("pathParameters", {}).get("bracelet_id", None)
    print("Requested metrics for bracelet", bracelet_id)

    query_string_parameters = event.get("queryStringParameters", dict())
    if query_string_parameters is None:
        print("No query string params found. Using defaults")
        query_string_parameters = dict()

    metric = query_string_parameters.get("metric", "")
    time_from = query_string_parameters.get("from", "1d")

    query = build_query(
        os.getenv("TIMESTREAM_DB"),
        os.getenv("TIMESTREAM_TABLE"),
        bracelet_id,
        metric,
        time_from
    )
    print("Start querying database")
    querier = TimestreamQuerier(timestream)
    result = querier.exec(query)
    print("Got result")
    print("Result type", type(result))

    return Ok(body=result[0])
