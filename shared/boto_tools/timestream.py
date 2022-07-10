from typing import Dict, List

import boto3
from mypy_boto3_timestream_query.client import TimestreamQueryClient
from mypy_boto3_timestream_query.paginator import QueryPaginator
from mypy_boto3_timestream_query.type_defs import RowTypeDef, DatumTypeDef, QueryResponseTypeDef

QueryResult = Dict[str, any]


class TimestreamQuerier:
    def __init__(self):
        self.client: TimestreamQueryClient = boto3.client('timestream-query')
        self.paginator: QueryPaginator = self.client.get_paginator('query')

    def exec(self, query: str) -> List[QueryResult]:
        try:
            page_iterator = self.paginator.paginate(QueryString=query)
            return [
                self._parse_query_result(page)
                for page in page_iterator
            ]
        except Exception as err:
            print(f"Exception while running query: {err}")

    def _print_query_status(self, query_status: dict[str, int]) -> None:
        progress_percentage = query_status["ProgressPercentage"]
        print(f"Query progress so far: {progress_percentage}%")

        bytes_scanned = float(query_status["CumulativeBytesScanned"]) / 10 ** 9
        print(f"Data scanned so far: {bytes_scanned} GB")

        bytes_metered = float(query_status["CumulativeBytesMetered"]) / 10 ** 9
        print(f"Data metered so far: {bytes_metered} GB")

    def _parse_query_result(self, query_result: QueryResponseTypeDef) -> QueryResult:
        self._print_query_status(query_result["QueryStatus"])

        column_info = query_result['ColumnInfo']

        parsed_result = dict(
            metadata=column_info,
            data=list()
        )

        for row in query_result["Rows"]:
            parsed_result["data"].append(
                self._parse_row(row, column_info)
            )

        return parsed_result

    def _parse_row(self, row: RowTypeDef, column_info):
        data = row['Data']
        parsed_row = []
        for i in range(len(data)):
            info = column_info[i]
            datum: DatumTypeDef = data[i]
            parsed_row.append(
                self._parse_datum(info, datum)
            )

        merged = {
            k: v
            for d in parsed_row
            for k, v in d.items()
        }

        return merged

    def _parse_datum(self, info, datum: DatumTypeDef):
        if datum.get('NullValue', False):
            return {info["Name"]: None}

        column_type = info["Type"]
        if 'ScalarType' in column_type:
            return {info["Name"]: datum['ScalarValue']}
