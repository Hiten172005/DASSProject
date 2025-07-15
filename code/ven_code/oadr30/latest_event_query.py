from oadr30.vtn import VTNOps
import json
from datetime import datetime

def get_latest_event(base_url, client_id, client_secret, program_id=None):
    """
    Retrieve the latest event from the VTN.
    
    Args:
    - base_url (str): Base URL of the VTN server
    - client_id (str): Client ID for authentication
    - client_secret (str): Client secret for authentication
    - program_id (str, optional): Specific program ID to filter events
    
    Returns:
    - dict: The latest event, or None if no events found
    """
    try:
        # Initialize VTN connection
        vtn = VTNOps(
            base_url=base_url,
            client_id=client_id,
            client_secret=client_secret
        )
        
        # Get events (all or for specific program)
        events = vtn.get_events(program_id)
        
        if not events or len(events) == 0:
            print("No events found.")
            return None
        
        events_list = list(events)
        
        # Sort events by creation time (most recent first)
        sorted_events = sorted(
            events_list, 
            key=lambda x: datetime.fromisoformat(x.get('createdDateTime', '1970-01-01')), 
            reverse=True
        )
        
        latest_event = sorted_events[0]
        

        print("Latest VTN Event:")
        print(json.dumps(latest_event, indent=2))
        
        return latest_event
    
    except Exception as ex:
        print(f"Error retrieving latest event: {ex}")
        return None

def extract_and_print_prices(event):
    """
    Extract and print prices from the event intervals
    
    Args:
    - event (dict): The event dictionary
    """
    if not event:
        print("No event provided to extract prices.")
        return
    
    print("\n--- Price Information ---")
    
    # Check for intervals
    intervals = event.get('intervals', [])
    if not intervals:
        print("No intervals found in the event.")
        return
    
    # Iterate through intervals and extract prices
    for i, interval in enumerate(intervals, 1):
        print(f"\nInterval {i}:")
        
        # Look for payload descriptors
        payload_descriptors = event.get('payloadDescriptors', [])
        for descriptor in payload_descriptors:
            print(f"Payload Descriptor: {json.dumps(descriptor, indent=2)}")
        
        # Extract payloads
        payloads = interval.get('payloads', [])
        for j, payload in enumerate(payloads, 1):
            print(f"  Payload {j}:")
            print(f"    Type: {payload.get('type', 'N/A')}")
            
            # Extract values
            values = payload.get('values', [])
            if values:
                print(f"    Values: {values}")
            
            # Additional payload details
            print(f"    Payload Details: {json.dumps(payload, indent=2)}")

def main():
    base_url = "http://localhost:3000"
    client_id = "admin"
    client_secret = "admin"
    program_id = "0"  
    
    latest_event = get_latest_event(
        base_url, 
        client_id, 
        client_secret, 
        program_id
    )
    
    if latest_event:
        print("\nEvent Details:")
        print(f"Event ID: {latest_event.get('id')}")
        print(f"Created At: {latest_event.get('createdDateTime')}")
        print(f"Program ID: {latest_event.get('programID')}")
        
        # Extract and print prices
        extract_and_print_prices(latest_event)

if __name__ == "__main__":
    main()