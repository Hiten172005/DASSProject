import oadr30
from oadr30.vtn import VTNOps
from oadr30.events import *
import random
from datetime import datetime,timezone
from oadr30.interval import IntervalPeriod, Interval
from datetime import timedelta
from flask import Flask


base_url = "http://98.70.52.255"
auth_url = "/auth/token"
client_id = "admin"  # Changed to ven-manager
client_secret = "admin"
vtn = VTNOps(base_url=base_url, auth_url=auth_url, client_id=client_id, client_secret=client_secret, auth_token_url_is_json=False )
program_id = "44f0d14e-4fa8-4274-b726-baa10efdd3a2"
print(f"Getting program '{program_id}'...")
program = vtn.get_program(program_id)



if not program:
    print(f"Program '{program_id}' not found, creating it...")
    print("all programs -- ")
    print(vtn.get_programs())
    program = vtn.create_program(program_id, programName="mainPriceProgram2",country="IN")
    if not program:
        print(f"Failed to create program '{program_id}'")
        exit(0)
    print(f"Successfully created program '{program_id}'")
else:
    print(f"Found existing program '{program_id}'")

## create fake events for the next 4 days (including today)
## 96 intervals spaced at 15 minutes
## corresponds to the standard industry format of 15 minute day ahead schedule.
## since charger limit is in hours ideally it should never query beyond next day. but by default return this day's schedule if next day not available.

"""{"createdDateTime":"2025-03-19T15:54:37.5326566+00:00","objectType":"EVENT","programID":"2380050f-c3f8-ec11-95d7-000d3afbedbd","payloadDescriptors":[{"payloadType":"PRICE","units":"KWH","currency":"USD"}],"intervalPeriod":{"start":"2025-03-19T15:00:00+00:00","duration":"PT1H"},"intervals":[{"id":0,"payloads":[{"type":"PRICE","values":[0.0106]}]},{"id":1,"payloads":[{"type":"PRICE","values":[0.0192]}]},{"id":2,"payloads":[{"type":"PRICE","values":[0.0309]}]},{"id":3,"payloads":[{"type":"PRICE","values":[0.0612]}]},{"id":4,"payloads":[{"type":"PRICE","values":[0.0925]}]},{"id":5,"payloads":[{"type":"PRICE","values":[0.1244]}]},{"id":6,"payloads":[{"type":"PRICE","values":[0.1667]}]},{"id":7,"payloads":[{"type":"PRICE","values":[0.2148]}]},{"id":8,"payloads":[{"type":"PRICE","values":[0.3563]}]},{"id":9,"payloads":[{"type":"PRICE","values":[0.4893]}]},{"id":10,"payloads":[{"type":"PRICE","values":[0.7098]}]},{"id":11,"payloads":[{"type":"PRICE","values":[0.7882]}]},{"id":12,"payloads":[{"type":"PRICE","values":[0.5586]}]},{"id":13,"payloads":[{"type":"PRICE","values":[0.3326]}]},{"id":14,"payloads":[{"type":"PRICE","values":[0.2152]}]},{"id":15,"payloads":[{"type":"PRICE","values":[0.1487]}]},{"id":16,"payloads":[{"type":"PRICE","values":[0.0864]}]},{"id":17,"payloads":[{"type":"PRICE","values":[0.0587]}]},{"id":18,"payloads":[{"type":"PRICE","values":[0.0385]}]},{"id":19,"payloads":[{"type":"PRICE","values":[0.0246]}]},{"id":20,"payloads":[{"type":"PRICE","values":[0.0165]}]},{"id":21,"payloads":[{"type":"PRICE","values":[0.0215]}]},{"id":22,"payloads":[{"type":"PRICE","values":[0.0359]}]},{"id":23,"payloads":[{"type":"PRICE","values":[0.0206]}]}]}"""



allevents = vtn.get_events(program_id)
if not allevents:
    print("No events found")
    allevents = Events([])
print("existing events")

for event in allevents:
    print(event['intervalPeriod']['start'])
    print("---")
dayx = datetime.now(timezone.utc) # IST +530
# change hour
dayx = dayx.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=2)
newEvents = Events([])
for i in range(5):
    day = dayx + timedelta(days=i)
    already_exists = False
    for eventx in allevents:
        if eventx['intervalPeriod']['start'] == day.isoformat():
            print(f"Event for {day.isoformat()} already exists")
            already_exists = True
            break
    if already_exists:
        continue
    
    event = {
        'createdDateTime': day.isoformat(), # start of the day
        'objectType': 'EVENT',
        'programID': program_id,
        'payloadDescriptors': [
            {
                'payloadType': 'PRICE',
                'units': 'KWH',
                'currency': 'INR'
            }
        ],
        'intervalPeriod': {
            'start': day.isoformat(),
            'duration': 'PT15M'
        },
        'intervals': []
    }
    for j in range(96):
        event['intervals'].append({
            'id': j,
            'payloads': [
                {
                    'type': 'PRICE',
                    'values': [random.uniform(10, 25)]
                }
            ]
        })
    newEvents.append(Event(event))
    print(f"Buffered create event for {day.isoformat()}")

vtn.create_events(newEvents)
allevents: list[Event] = vtn.get_events(program_id)
if not allevents:
    allevents = Events([])
print("new events added: " +str(len(newEvents)))
CACHE = {
    'lastCached': datetime.now(timezone.utc) - timedelta(days=1),
    'CACHE_LIMIT': timedelta(seconds=10)
}
priceEvents: list[Event] = []
def refreshPrices():
    global priceEvents
    if priceEvents == None or datetime.now(timezone.utc) - CACHE['lastCached'] > CACHE['CACHE_LIMIT']:
        priceEvents = vtn.get_events(program_id)
        CACHE['lastCached'] = datetime.now(timezone.utc)
        print("Refreshed prices")
        

app = Flask(__name__)
@app.route('/getPrices/<dmy>') #DD-MM-YYYY
def get_prices(dmy):
    day = datetime.strptime(dmy, "%d-%m-%Y")
    refreshPrices()

    day = day.replace(hour=0, minute=0, second=0, microsecond=0,tzinfo=timezone.utc)
    for event in priceEvents:
        print(event.getIntervalPeriod().getStartTime().dt, day)
        # use event as a type of Event
        if event.getIntervalPeriod().getStartTime().dt == day:
            prices = []
            for interval in event['intervals']:
                prices.append(interval['payloads'][0]['values'][0])
            return {"prices": prices}
    return {"prices": [15]*96}

# test 
print(get_prices("21-03-2025"))

# start server
if __name__ == '__main__':
   app.run(host="0.0.0.0",port=3000)