# program init
import apiaccessor
import credentials
import requests
import pprint
import json

pp = pprint.PrettyPrinter()
REGATTA_ID = '6033'
CLUB_ID = '1072'
RC_API_URL = 'https://api.regattacentral.com'

USERNAME = credentials.USERNAME
PASSWORD = credentials.PASSWORD
CLIENT_ID = credentials.CLIENT_ID
CLIENT_SECRET = credentials.CLIENT_SECRET

class Reader:
    def __init__(self):
        # authorization stuff
        self.oauth = apiaccessor.OAuth2(RC_API_URL + '/oauth2/api/token', RC_API_URL + '/oauth2/api/token', RC_API_URL + '/oauth2/api/validate', CLIENT_ID, CLIENT_SECRET)
        self.access_token = self.oauth.get_token(USERNAME,PASSWORD)
        self.headers = {'Authorization':self.access_token}
        self.reauthed = False

    def get_data(self, path):
        d = requests.get(RC_API_URL + path, headers=self.headers)
        print('data received')
        if d.status_code == 401 and self.reauthed == False:
            self.oauth.refresh_token()
            self.reauthed = True
            self.get_data(path)
        if d.status_code != 200:
            print(d.status_code)
            print(d.url)
        return json.loads(d.text)

r = Reader()

class Regatta:
    def __init__(self, regatta_id, club_id):
        print('started fetching data')
        # metadata
        data = r.get_data('/v4.0/regattas/' + REGATTA_ID)['data']
        self.name = data['name']
        self.rc_regatta_id = regatta_id
        self.rc_club_id = club_id
        self.dates = data['regattaDates']
        self.venue = data['venue']
        # events
        self.events = []
        offline_results = r.get_data('/v4.0/regattas/'+REGATTA_ID+'/offlineResults')
        if offline_results['count'] == 0:
            self.outside_timing = None
        else:
            self.outside_timing = offline_results['data'][0]['url']

    def find_relevant_entries(self,data):
        print('sorting entries')
        relevant_entry_ids = []
        for j in range(data['count']):
            if str(data['data'][j]['organization_id']) == CLUB_ID:
              relevant_entry_ids.append(data['data'][j]['entry_id'])
        return relevant_entry_ids

    def get_events(self):
      event_ids = []
      data = r.get_data('/v4.0/regattas/'+REGATTA_ID+'/events/')
      for i in range(len(data['data'])):
            event_ids.append(data['data'][i]['event_id'])
      return event_ids

    def find_relevant_events(self):
        print('sorting events')
        # this could be simplified but it sometimes crashes if it is simpler 
        temp = r.get_data('/v4.0/regattas/'+REGATTA_ID+'/organizations/'+CLUB_ID+'/events')
        events = temp['data']
        relevant_event_ids = []
        for i in range(len(events)):
            relevant_event_ids.append(events[i]['event_id'])
        return relevant_event_ids

    def build_events(self, build_all_events):
        all_events = r.get_data('/v4.0/regattas/'+REGATTA_ID+'/events')['data']
        if build_all_events is False:
            events_to_build = self.find_relevant_events()
        else:
            events_to_build = self.get_events()
        for i in range(len(events_to_build)):
            print('event_id: '+str(events_to_build[i]))
            events = []
            title = ''
            sequence = 0
            final_race_time = 0
            coxed = False
            for j in range(len(all_events)):
                if all_events[j]['event_id'] == events_to_build[i]:
                    title = all_events[j]['title']
                    sequence = all_events[j]['sequence']
                    final_race_time = all_events[j]['finalRaceTime']
                    coxed = all_events[j]['coxed']
                e = Event(events_to_build[i],title,sequence,final_race_time,coxed)
                events.append(e)
        self.events = events
        return events

    def dump(self):
        print(self.name)
        print(self.dates)
        print(self.venue)
        print(self.events)
        print(self.outside_timing)


class Event:
    def __init__(self, event_id, title, sequence, final_race_time, coxed):
        self.event_id = str(event_id)
        self.title = title
        self.sequence = sequence
        self.final_race_time = final_race_time
        self.coxed = coxed
        self.entries = self.build_entries() # list of Entry objects
        self.relevant_entries = self.find_relevant_entries() # list of relevant entry_ids

    def build_entries(self):
        data = r.get_data('/v4.0/regattas/'+REGATTA_ID+'/events/'+self.event_id+'/entries')['data']
        entries = []
        for i in range(len(data)):
            e = Entry(self.event_id,data[i]['entry_id'],data[i]['entryLabel'])
            entries.append(e)
            print(str(data[i]['entry_id'])+', '+data[i]['entryLabel'])
            i += 1
        return entries

    def get_entry_list(self):
        data = r.get_data('/v4.0/regattas/'+REGATTA_ID+'/events/'+self.event_id+'/entries')['data']
        entries = []
        for i in range(len(data)):
            entries.append(data[i]['entry_id'])
        return entries

    def find_relevant_entries(self):
        data = r.get_data('/v4.0/regattas/'+REGATTA_ID+'/events/'+self.event_id+'/entries')
        relevant_entry_ids = []
        for j in range(data['count']):
            if str(data['data'][j]['organization_id']) == CLUB_ID:
                relevant_entry_ids.append(data['data'][j]['entry_id'])
        return relevant_entry_ids

    def dump(self):
        print(self.event_id)
        print(self.title)
        print(self.sequence)
        print(self.final_race_time)
        print(self.coxed)
        print(self.entries)
        print(self.relevant_entries)


class Entry:
    def __init__(self, event_id, entry_id, label):
        self.event_id = event_id
        self.entry_id = entry_id
        self.organization_id = CLUB_ID
        self.lane = self.get_lane(self.entry_id)
        self.lineup = self.get_lineup(self.entry_id)
        self.label = label
        self.position = 0
        self.time_elapsed = 0.0

    def write_results(self,position,time_elapsed):
        self.position = position
        self.time_elapsed = time_elapsed

    def get_lane(self,entry_id):
        try:
            lane_data = r.get_data('/v4.0/regattas/'+REGATTA_ID+'/events/'+entry_id+'/lanes')['data'][0]['races'][0]['lanes']
            for i in range(len(lane_data)):
                if lane_data[i]['entry_id'] == entry_id:
                    return lane_data[i]['lane']
        except TypeError:
            return None

    def get_lineup(self, entry_id):
        try:
            lineup = []
            for i in range(len(r.get_data('/v4.0/regattas/'+REGATTA_ID+'/entries/'+entry_id)['data']['entryParticipants'])):
                lineup.append(r.get_data('/v4.0/regattas/'+REGATTA_ID+'/entries/'+entry_id)['data']['entryParticipants'][i]['name'])
            return lineup
        except TypeError:
            return None

    def update(self, event_id, entry_id, label):
        if event_id != self.event_id:
            self.event_id = event_id
        if entry_id != self.entry_id:
            self.entry_id = entry_id
        if label != self.label:
            self.label = label
        if self.get_lane(self.entry_id) != self.lane:
            self.lane = self.get_lane(self.entry_id)
        if self.get_lineup(self.entry_id) != self.lineup:
            self.lineup = self.get_lineup(self.entry_id)

    def dump(self):
        print(self.event_id)
        print(self.entry_id)
        print(self.organization_id)
        print(self.lane)
        print(self.lineup)
        print(self.label)
        print(self.position)
        print(self.time_elapsed)
