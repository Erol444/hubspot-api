import requests
from typing import Dict
from .login import Login

class ApiClient:
    def __init__(self, login: Login):
        self.login = login
        self.update_headers()

    def api_call(self, method: str, endpoint: str, params: Dict = None, data: Dict = None):
        url = self.login.domain.replace('app', 'api') + endpoint

        if params == None:
            params = dict()
        params['portalId'] = self.login.portalId

        # print(f'Sending {method} request to {url}, params: {params}')

        response = requests.request(method,
                                    url,
                                    headers=self.headers,
                                    json=data,
                                    cookies=self.login.cookie_jar,
                                    params=params)
        return response

    def update_headers(self):
        self.headers = {
            'accept-encoding': 'gzip, deflate',
            'authority': self.login.domain,
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'accept-language': 'en-US,en;q=0.9',
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'user-agent': 'HubSpotAndroid/3.54.1 (build:3.54.1; Android 11)',
            'x-hubspot-language': 'en',
            'x-hubspot-mobileapp': 'Android',
            'x-source': 'CRM_UI',
            'x-hs-user-request': '1',
            'x-sourceid': f'userId:{self.login.userId}',
            'x-hubspot-csrf-hubspotapi': self.login.csrfToken,
            'content-type': 'application/json; charset=UTF-8',
        }