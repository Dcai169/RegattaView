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
    print('token requested')
    # get a token
    try:
      t = json.loads(requests.post(APIurl+'/oauth2/api/token', data = {'client_id':self.client_id,'client_secret':self.client_secret,'username':self.username,'password':self.password,'grant_type':'password'}).text)
    # Catch the error
    except json.decoder.JSONDecodeError:
      print(requests.post(APIurl+'/oauth2/api/token', data = {'client_id':self.client_id,'client_secret':self.client_secret,'username':self.username,'password':self.password,'grant_type':'password'}).text)
    # write token to variables
    print('token received')
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


class Regatta:
    def __init__(self):
        print('started fetching data')
        # authorization stuff
        self.oauth = OAuth()
        self.access_token = self.oauth.gettoken()
        self.headers = {'Authorization':self.access_token}
        self.reauthed = False
        # metadata
        data = r.getdata('/v4.0/regattas/' + regattaID)['data']
        self.name = data['name']
        self.dates = data['regattaDates']
        self.venue = data['venue']
    def getdata(self, path):
        d = requests.get(APIurl+path,headers=self.headers)
        print('data received')
        if d.status_code == 401 and self.reauthed == False:
            self.oauth.refreshtoken()
            self.reauthed = True
            self.getData(path)
        if d.status_code != 200:
            print(d.status_code)
            print(d.url)
        return json.loads(d.text)
  
    def getevents(self,data):
        event_ids = []
        for i in range(len(data['data'])):
            event_ids.append(data['data'][i]['eventId'])
        return event_ids

    def findrelevantevents(self,data,clubid):
        print('sorting events')
        event_ids = self.getevents(data)
        relevant_event_ids = []
        for i in range(len(event_ids)):
            t = self.getdata('/v4.0/regattas/'+regattaID+'/events/'+str(event_ids[i])+'/entries')
            for j in range(t['count']):
                if str(t['data'][j]['organizationId']) == clubid:
                    relevant_event_ids.append(event_ids[i])
        return relevant_event_ids

    def findrelevantentries(self,data,clubid):
        print('sorting entries')
        relevant_entry_ids = []
        for j in range(data['count']):
            if str(data['data'][j]['organizationId']) == clubid:
              relevant_entry_ids.append(data['data'][j]['entryId'])
        return relevant_entry_ids

class Event:
    def __init__(self, eventid, title, sequence, final_race_time, coxed, entries, relevant_entries):
        self.eventid = eventid
        self.title = title
        self.sequence = sequence
        self.final_race_time = final_race_time
        self.coxed = coxed
        self.entries = entries
        self.relevant_entries = relevant_entries

    def update(self):
        pass # write me too

class Entry:
    def __init__(self, entryid, label, lineup, bow):
        self.r = Regatta()
        self.lineup = lineup
        self.bow = bow
        self.entryid = entryid
        self.organizationid = clubID
        self.lanes = self.getlane(r.getdata('/v4.0/regattas/' + regattaID + '/events/'),self.entryid)
        self.label = label
        self.position = 0
        self.duration = 0.0

    def getresults(self,position,duration):
        self.position = position
        self.duration = duration

    def getlane(self, data, entryid):
        try:
            laneslist = data['data'][0]['races'][0]['lanes']
            for i in range(len(laneslist)):
                if laneslist[i]['entryId'] == entryid:
                    return laneslist[i]['lane']
        except IndexError:
            return None
        else:
            return 0


r = Regatta()
print('\n'+'='*25+'\n')
pp.pprint(r.getdata('/v4.0/regattas/' + regattaID)['data'])
