import commonclasses
import pprint
pp = pprint.PrettyPrinter()

def parse_hnevent(event_data):
    id_ = event_data['ID']
    title = event_data['Name']
    sequence = event_data['Ordering']
    straight = False
    if '+' in event_data['Name']:
        straight = True
    e = commonclasses.HNEvent(id_, title, sequence, straight)
    return e

def parse_hnentries(entries_data, entry_list):
    # Need to figure out how to figure out iterations are necessary
    for event in entries_data:
        number_entries = len(event['EntryResults'])
        for entries in event['EntryResults']:
            if len(entries) > 1:
                data = entries['Entry']
                event_id = data['EventId']
                entry_id = data['Id']
                name = data['Name']
                e = commonclasses.HNEntry(event_id, entry_id, name)
                entry_list.append(e)
