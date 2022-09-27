import requests
import json

from time import time
from requests.auth import HTTPBasicAuth

class Kobo(object):
    def __init__(self, username: str, password: str, **kwargs):
        self.username = username
        self.password = password

        self.url = kwargs.get("url", "https://kf.kobotoolbox.org")
        self.time_to_stale = kwargs.get("time_to_stale", 300)
        
        self.token = None
        self.token_refresh_time = -float("inf")
        self.api = 'api/v2'

    def _need_new_token(self):
        return time() - self.token_refresh_time >= self.time_to_stale

    def _get_new_token(self):
        response = requests.get(
            f'{self.url}/token?format=json', 
            auth=HTTPBasicAuth(self.username, self.password)
        )
        self.token = response.json()['token']
        self.auth_headers = {"Authorization": f"Token {self.token}"}
        self.token_refresh_time = time()

    def ensure_authorized(method):
        def check_auth_then_run_method(self, *args, **kwargs):
            if self._need_new_token():
                self._get_new_token()
            return method(self, *args, **kwargs)

        return check_auth_then_run_method

    @ensure_authorized
    def pull_data(self, uid):
        response = requests.get(
            f'{self.url}/{self.api}/assets/{uid}/data.json',
            headers=self.auth_headers
        )
        print(response.json())
        return response.json()["results"]
