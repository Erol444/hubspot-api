import requests
import json
import pickle
import uuid
from typing import Callable
from pathlib import Path
from http.cookies import SimpleCookie

class Login:
    def __init__(self, email: str, password: str, verification_code_cb: Callable):
        self.email = email
        self.password = password
        self.verification_code_cb = verification_code_cb

        # Check if login.pkl exists. If it does, open it
        if Path('login.pkl').exists():
            with open('login.pkl', 'rb') as file:
                vals = pickle.load(file)

                def parse_cookies(cookie_string) -> requests.cookies.RequestsCookieJar:
                    cookie_jar = requests.cookies.RequestsCookieJar()
                    # Split the string into individual cookie strings
                    cookies = cookie_string.split(", ")
                    for cookie in cookies:
                        # Parse each cookie string
                        simple_cookie = SimpleCookie()
                        simple_cookie.load(cookie)
                        for key, morsel in simple_cookie.items():
                            # Add each cookie to the jar
                            cookie_jar.set(key, morsel.value, domain=morsel['domain'], path=morsel['path'], secure=morsel['secure'])
                    return cookie_jar
                # Create a RequestsCookieJar from the SimpleCookie
                self.cookie_jar = parse_cookies(vals['cookie_header'])
                self.csrfToken = vals['csrfToken']
                self.userId = vals['userId']
                self.accounts = vals['accounts']
                self.domain = self.accounts[0]['appDomain']
                self.portalId = self.accounts[0]['id']
        else:
            self.login()

    def login(self):
        url = "https://api.hubspot.com/login-api/v1/login/mobile"
        headers = {
            'accept-encoding': 'gzip',
            'user-agent': 'HubSpotAndroid/3.54.1 (build:3.54.1; Android 11)',
            'x-hubspot-language': 'en',
            'x-hubspot-mobileapp': 'Android',
            'x-source': 'CRM_UI',
            'content-type': 'application/json; charset=UTF-8',
        }
        payload = {
            "deviceId": uuid.uuid4().hex,
            "email": self.email,
            "loginPortalId": "",
            "password": self.password,
            "rememberLogin": True
        }
        response = requests.post(url,
                        headers=headers,
                        json=payload)

        # Check status
        if response.status_code == 400:
            raise Exception(response.text)

        # If we need additional verification, call the callbacks
        parsed_response = json.loads(response.text)


        # TWO_FACTOR_ENFORCED_ON_HUB
        if parsed_response['status'] in ['SUSPICIOUS_USER_MUST_CONFIRM', 'TWO_FACTOR_REQUIRED']:
            url = 'https://api.hubspot.com/login-api/v1/login/mobile/verification-code'
            data = {
                "email": "erol123444@gmail.com",
                "shouldRememberThisDevice": True,
                "token": parsed_response['token'],
                "verificationCode": self.verification_code_cb()
            }
            # In case of 2FA
            if parsed_response['status'] == 'TWO_FACTOR_REQUIRED':
                data['twoFactorLevel'] = 'PRIMARY'

            response = requests.post(url,
                        headers=headers,
                        json=data)
            if response.status_code == 400:
                raise Exception(response.text)
            parsed_response = json.loads(response.text)


        self.cookie_jar = response.cookies
        self.domain = parsed_response['accounts'][0]['appDomain']
        self.csrfToken = parsed_response['csrfToken']
        self.userId = parsed_response['userId']
        self.accounts = parsed_response['accounts']
        self.portalId = parsed_response['accounts'][0]['id']

        with open('login.pkl', 'wb') as file:
            pickle.dump({
                'userId': self.userId,
                'csrfToken': self.csrfToken,
                'cookie_header': response.headers.get('Set-Cookie'),
                'accounts': self.accounts,
            }, file)
