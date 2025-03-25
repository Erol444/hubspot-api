import requests
from typing import Dict, Any

class ApiResponse:
    def __init__(self, response: requests.Response):
        self.raw = response
        self.text = response.text
        self.status_code: int = response.status_code
        # If status code doesn't start with 2, don't do .json()
        if self.status_code // 100 != 2:
            self.data = None
        else:
            self.data: Dict = response.json()

class ApiClient:
    def __init__(self, token: str):
        self.token = token
        self.acc_info = None

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

    def get_acc_info(self) -> Dict[str, Any]:
        if self.acc_info:
            return self.acc_info.data
        self.acc_info = self.api_call("GET", "/account-info/v3/details")
        return self.acc_info.data
