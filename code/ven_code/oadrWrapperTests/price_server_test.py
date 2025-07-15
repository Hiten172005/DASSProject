from oadr30.vtn import VTNOps
from oadr30.log import oadr3_log_critical
from oadr30.price_server_client import PriceServerClient
from oadr30.config import OADR3Config, OlivinePriceServer
from oadr30.scheduler import EventScheduler
from oadr30.values_map import ValuesMap
import json, time, traceback

def get_events(events_obj):
    """
    Returns a list of event dictionaries from the events object.
    
    Parameters:
    - events_obj: The events object from the price server
    
    Returns:
    - List of event dictionaries containing event data
    """
    # Based on the printout, it seems events is already a list of dictionaries
    # So we can simply return it as is
    if hasattr(events_obj, 'num_events'):
        # If events_obj has a built-in method to get events, use it
        return events_obj.events  # Assuming there's an 'events' property or method
    else:
        # Otherwise, just return the object if it's already a list
        return events_obj


def modify_events(events):
    """
    Modify specific aspects of the events data before sending to VTN.
    
    Parameters:
    - events: The events object from the price server
    """
    # Get events in a way that works with your actual structure
    events_list = events
    
    # Process each event
    for event in events_list:
        # Modify program ID
        event['programID'] = 'a20354f7-a4fe-ee11-aaf0-002248c1ffa5'
        
        # Scale all price values by a factor
        for interval in event['intervals']:
            for payload in interval['payloads']:
                if payload['type'] == 'PRICE':
                    payload['values'][0] *= 1.1  # Increase prices by 10%
    
    return events_list


def scheduler_callback(segment:ValuesMap):
    print(segment)

def scheduler_future_callback(segment:ValuesMap):
    print(segment)

def main():
    try:
        OADR3Config.duration_scale = 1/360
        OADR3Config.events_start_now = True
        
        # Get events from Olivine price server
        client = PriceServerClient(OlivinePriceServer.getUrl('hourly', 'fall', 'price'))
        events = client.getEvents()

        print("Before is ",events)

        modify_events(events) # In case you want to update prices, schedule etc which you receive Olivine url, then modify the modify_events function according to your need. We can also implement terminal input.


        print("After is",events)

        client = PriceServerClient(OlivinePriceServer.getUrl('hourly', 'fall', 'ghg'))
        ghgEvents = client.getEvents()
        
        events.appendEvents(ghgEvents)  # combine them

        # print(events)
        
        # Connect to your local VTN server
        base_url = "http://localhost:3000"
        auth_url = "/auth/token"
        client_id = "admin"  # Changed to ven-manager
        client_secret = "admin"
        
        print(f"Connecting to VTN at {base_url}")
        
        vtn = VTNOps(
            base_url=base_url,
            auth_url=auth_url,
            client_id=client_id,
            client_secret=client_secret,
            auth_token_url_is_json=False
        )
        
        # Use program ID "0"
        program_id = "0"
        
        print(f"Getting program '{program_id}'...")
        program = vtn.get_program(program_id)
        
        if not program:
            print(f"Program '{program_id}' not found, creating it...")
            program = vtn.create_program(program_id, programName="Default Program")
            if not program:
                print(f"Failed to create program '{program_id}'")
                return
            print(f"Successfully created program '{program_id}'")
        else:
            print(f"Found existing program '{program_id}'")
        
        # Create events
        print(f"Creating events in program '{program_id}'...")
        success = vtn.create_events(events)
        if success is not False:  # Check if not explicitly False
            print("Events created successfully")
        else:
            print("Failed to create events")
        
    except Exception as ex:
        print(f"Error: {ex}")
        traceback.print_exc()
        oadr3_log_critical("main failed")

if __name__ == "__main__":
    main()