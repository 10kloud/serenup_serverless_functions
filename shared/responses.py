import json
from typing import Union, Dict, List

default_headers: Dict[str, str] = {
    "Access-Control-Allow-Origin": "*",
}


class Response(dict):
    def __init__(self, status_code: int, headers: Dict[str, str], body: Union[str, dict, List]):
        dict.__init__(self,
                      statusCode=status_code,
                      headers=default_headers | headers,
                      body=body if type(body) is str else json.dumps(body)
                      )


class Ok(Response):
    def __init__(self, headers: Dict[str, str] = {}, body: Union[str, dict, List] = "OK"):
        super().__init__(200, headers, body)


class BadRequest(Response):
    def __init__(self, headers: Dict[str, str] = {}, body: Union[str, dict, List] = "Bad Request"):
        super().__init__(400, headers, body)


class ResourceNotFound(Response):
    def __init__(self, headers: Dict[str, str] = {}, body: Union[str, dict, List] = "Resource not found"):
        super().__init__(404, headers, body)


class Gone(Response):
    def __init__(self, headers: Dict[str, str] = {}, body: Union[str, dict, List] = "Gone"):
        super().__init__(410, headers, body)
