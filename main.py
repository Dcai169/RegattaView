# program init
from time import sleep
from time import time
import requests
import pprint
import json
global regattaID
global clubID
pp = pprint.PrettyPrinter()
regattaID = '6033'
clubID = '1072'
APIurl = 'https://api.regattacentral.com'


class OAuth:
  def __init__(self):
    # client credentials
    self.client_id = '2cda3093-3efd-4ffd-933d-f95a4fd02ec6'
    self.client_secret = 'r0WWayWest'
    self.username = 'dcai169'
    self.password = '77PxNIfR6rvekj76'
    # token data
    self.access_token = ''
    self.expiry_time = 0
    self.refresh_token = ''
  
  def gettoken(self):
    print('get token')
    # get a token
    try:
      t = json.loads(requests.post(APIurl+'/oauth2/api/token', data = {'client_id':self.client_id,'client_secret':self.client_secret,'username':self.username,'password':self.password,'grant_type':'password'}).text)
    # Catch the error
    except json.decoder.JSONDecodeError:
      print(requests.post(APIurl+'/oauth2/api/token', data = {'client_id':self.client_id,'client_secret':self.client_secret,'username':self.username,'password':self.password,'grant_type':'password'}).text)
    # write token to variables
    self.access_token = t['access_token']
    self.expiry_time = t['expires_in'] + time()
    self.refresh_token = t['refresh_token']
    # return token
    return t['access_token']


  def refreshtoken(self):
    print('refresh token')
    # refresh token after an hour
    try:
      t = json.loads(requests.post(APIurl+'/oauth2/api/token', data = {'client_id':self.client_id,'client_secret':self.client_secret, 'refresh_token':self.refresh_token, 'grant_type':'refresh_token'}).text)
    except json.decoder.JSONDecodeError:
      print(requests.post(APIurl+'/oauth2/api/token', data = {'client_id':self.client_id,'client_secret':self.client_secret,'refresh_token':self.refresh_token,'grant_type':'refresh_token'}).text)
    else:
      self.expiry_time = t['expires_in'] + time()
      self.access_token = t['access_token']
  def validatetoken(self):
    t = json.loads(requests.post(APIurl+'/oauth2/api/validate', data = {'token':self.access_token}).text)
    if 'error' in t:
      return False
    else:
      return True


class Main:
  def __init__(self):
    self.oauth = OAuth()
    self.access_token = self.oauth.gettoken()
    self.headers = {'Authorization':self.access_token}
    self.reauthed = False

  def getdata(self, path, terms):
    d = requests.get(APIurl+path+terms,headers=self.headers)
    if d.status_code == 401 and self.reauthed == False:
      self.oauth.refreshtoken()
      self.reauthed = True
      self.getData(path, terms)
    if d.status_code != 200:
      print(d.status_code)
    return json.loads(d.text)

  def findrelevantevents(self,data,clubid):
      event_ids = []
      relevant_event_ids = []
      for i in range(len(data['data'])):
          event_ids.append(data['data'][i]['eventId'])
      print(event_ids)
      for i in range(len(event_ids)):
          t = self.getdata('/v4.0/regattas/'+regattaID+'/events/'+str(event_ids[i])+'/entries', '')
          for j in range(t['count']):
              if str(t['data'][j]['organizationId']) == clubid:
                  relevant_event_ids.append(event_ids[i])
      return relevant_event_ids

class Event:
    def __init__(self):
        self.number = ""
        self.title = ""
        self.final_race_time = 0
        self.entries = {}
        self.relevant_entries = {}


r = Main()
r.findrelevantevents(r.getdata('/v4.0/regattas/'+regattaID+'/events/', ''),clubID)
pp.pprint(r.getdata('/v4.0/regattas/'+regattaID+'/events/', ''))
# pp.pprint(r.getdata('/v4.0/regattas/'+regattaID+'/events/6/entries', ''))
