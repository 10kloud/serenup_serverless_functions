import itertools
from pprint import pprint
from typing import Iterable


class TimestreamQuery:
    def __init__(self, client):
        self.client = client
        self.paginator = client.get_paginator('query')

    def run_query(self, query_string):
        try:
            page_iterator = self.paginator.paginate(QueryString=query_string)
            parsed_results = []
            for page in page_iterator:
                parsed_results.append(
                    self._parse_query_result(page)
                )

            return parsed_results
        except Exception as err:
            print("Exception while running query:", err)

    def _parse_query_result(self, query_result, group_data_interval: int = 1):
        query_status = query_result["QueryStatus"]

        progress_percentage = query_status["ProgressPercentage"]
        print(f"Query progress so far: {progress_percentage}%")

        bytes_scanned = float(query_status["CumulativeBytesScanned"]) / 10 ** 9
        print(f"Data scanned so far: {bytes_scanned} GB")

        bytes_metered = float(query_status["CumulativeBytesMetered"]) / 10 ** 9
        print(f"Data metered so far: {bytes_metered} GB")

        column_info = query_result['ColumnInfo']

        parsed_result = dict(
            metadata=column_info,
            data=list()
        )
        # print("Metadata: %s" % column_info)
        # print("Data: ")
        for row in query_result['Rows']:
            print("foreach row in query_result:", row)
            parsed_result["data"].append(self._parse_row(column_info, row))
            # print(self._parse_row(column_info, row))

        return parsed_result

    def _parse_row(self, column_info, row, n_at_a_time: int = 1):
        data = row['Data']
        row_output = []
        for j in range(len(data)):
            info = column_info[j]
            datum = data[j]
            row_output.append(self._parse_datum(info, datum))

        # merged = {}
        # row_output = iter(row_output)
        # for item in row_output:
        #     merged = item | next(row_output)

        # print("Inside _parse_row:", merged)
        # return merged
        # # return "{%s}" % str(row_output)

        merged = {}
        row_output = iter(row_output)
        for item in row_output:
            partially_merged = item
            for i in range(n_at_a_time):
                partially_merged = partially_merged | next(row_output)
            merged |= partially_merged
        return merged


    def _parse_datum(self, info, datum):
        if datum.get('NullValue', False):
            return "%s=NULL" % info['Name'],

        column_type = info['Type']

        # If the column is of TimeSeries Type
        if 'TimeSeriesMeasureValueColumnInfo' in column_type:
            return self._parse_time_series(info, datum)

        # If the column is of Array Type
        elif 'ArrayColumnInfo' in column_type:
            array_values = datum['ArrayValue']
            return "%s=%s" % (info['Name'], self._parse_array(info['Type']['ArrayColumnInfo'], array_values))

        # If the column is of Row Type
        elif 'RowColumnInfo' in column_type:
            row_column_info = info['Type']['RowColumnInfo']
            row_values = datum['RowValue']
            return self._parse_row(row_column_info, row_values)

        # If the column is of Scalar Type
        else:
            r = {self._parse_column_name(info): datum['ScalarValue']}
            return r

    def _parse_time_series(self, info, datum):
        time_series_output = []
        for data_point in datum['TimeSeriesValue']:
            time_series_output.append("{time=%s, value=%s}"
                                      % (data_point['Time'],
                                         self._parse_datum(info['Type']['TimeSeriesMeasureValueColumnInfo'],
                                                           data_point['Value'])))
        return "[%s]" % str(time_series_output)

    def _parse_array(self, array_column_info, array_values):
        array_output = []
        for datum in array_values:
            array_output.append(self._parse_datum(array_column_info, datum))

        return "[%s]" % str(array_output)

    @staticmethod
    def _parse_column_name(info):
        if 'Name' in info:
            return info['Name']
        else:
            return ""
