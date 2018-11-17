import json
from time import time
import requests

class OAuth2:
    # The OAuth2 class handles OAuth2 Authentication
    def __init__(self, api_url, client_id, client_secret, username, password):
        self.api_url = api_url
        # client credentials
        # username and password should be user input
        # client_id and client_secret should be hardcoded
        self.client_id = client_id
        self.client_secret = client_secret
        self.username = username
        self.password = password
        # token data
        self.access_token = ''
        self.expires_at = 0
        self.refresh_token = ''

    def get_token(self):
        # This requests and receives a token from the server
        # returns access token

        # requests a token
        try:
            t = json.loads(requests.post(self.api_url+'/oauth2/api/token', data = {'client_id':self.client_id,'client_secret':self.client_secret,'username':self.username,'password':self.password,'grant_type':'password'}).text)
        # If a token is not issued, catch the error
        except json.decoder.JSONDecodeError:
            print(requests.post(self.api_url+'/oauth2/api/token', data = {'client_id':self.client_id,'client_secret':self.client_secret,'username':self.username,'password':self.password,'grant_type':'password'}).text)
        # write token to memory
        print('token received')
        self.access_token = t['access_token']
        self.expires_at = t['expires_in'] + time()
        self.refresh_token = t['refresh_token']
        # return token
        return t['access_token']

    def refresh_token(self):
        # This will refresh the token if the token has expired
        # returns nothing, write the token to memory
        print('refresh token')
        # refresh token after an hour
        try:
            t = json.loads(requests.post(self.api_url+'/oauth2/api/token', data = {'client_id':self.client_id,'client_secret':self.client_secret, 'refresh_token':self.refresh_token, 'grant_type':'refresh_token'}).text)
        except json.decoder.JSONDecodeError:
            print(requests.post(self.api_url+'/oauth2/api/token', data = {'client_id':self.client_id,'client_secret':self.client_secret,'refresh_token':self.refresh_token,'grant_type':'refresh_token'}).text)
        else:
            self.expires_at = t['expires_in'] + time()
            self.access_token = t['access_token']

    def validate_token(self):
        # This will check if the token is valid or not
        # returns a boolean based on the validity of the token
        t = json.loads(requests.post(self.api_url+'/oauth2/api/validate', data = {'token':self.access_token}).text)
        if 'error' in t:
          return False
        else:
          return True

