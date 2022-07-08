import json
from typing import Union, Dict

default_headers: Dict[str, str] = {
    "Access-Control-Allow-Origin": "*",
}


class Response(dict):
    def __init__(self, status_code: int, headers: Dict[str, str], body: Union[str, dict]):
        dict.__init__(self,
                      statusCode=status_code,
                      headers=default_headers | headers,
                      body=body if type(body) is str else json.dumps(body)
                      )


class Ok(Response):
    def __init__(self, headers: Dict[str, str] = {}, body: Union[str, dict] = "OK"):
        super().__init__(200, headers, body)


class BadRequest(Response):
    def __init__(self, headers: Dict[str, str] = {}, body: Union[str, dict] = "Bad Request"):
        super().__init__(400, headers, body)
