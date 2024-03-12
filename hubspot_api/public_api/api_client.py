import requests
from typing import Dict

class ApiResponse:
    def __init__(self, response: requests.Response):
        self.raw = response
        self.text = response.text
        self.data: Dict = response.json()
        self.status_code: int = response.status_code

class ApiClient:
    def __init__(self, token: str):
        self.token = token

    def api_call(self, method: str, endpoint: str, params: Dict=None, data: Dict = None, headers: Dict=None) -> ApiResponse:
        if headers == None:
            headers = dict()
        headers['accept'] = "application/json"
        headers['authorization'] = f"Bearer {self.token}"
        if data is not None:
            headers['content-type'] = "application/json"
        url = f"https://api.hubapi.com{endpoint}"

        reqRes = requests.request(method, url, headers=headers, params=params, json=data)
        res = ApiResponse(reqRes)
        return res