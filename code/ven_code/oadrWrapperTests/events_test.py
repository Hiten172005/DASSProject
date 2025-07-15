from oadr30.vtn import VTNOps
from oadr30.log import oadr3_log_critical
from oadr30.price_server_client import PriceServerClient
from oadr30.config import OADR3Config, OlivinePriceServer, VTNRefImpl
from oadr30.scheduler import EventScheduler
from oadr30.values_map import ValuesMap
from oadr30.ven import Resource
import json,time


def scheduler_callback(segment:ValuesMap):
    print (segment)

def scheduler_future_callback(segment:ValuesMap):
    print (segment)

def main(base_url:str, auth_url:str, client_id:str, client_secret:str, ven_name:str):
    try:
        OADR3Config.duration_scale = 1/360
        OADR3Config.events_start_now = True
        
        # Set the values for your local VTN
        if base_url is None:
            base_url = "http://localhost:3000"
        if auth_url is None:
            auth_url = "/auth/token"  # Just the path component
        if client_id is None:
            client_id = "ven-manager"  # Changed from "ven-1" to "ven-manager"
        if client_secret is None:
            client_secret = "ven-manager"  # Changed from "ven-1" to "ven-manager"
            
        print(f"Connecting to VTN at {base_url} with auth path {auth_url}")
        print(base_url, auth_url, client_id, client_secret)
        print("/n")
        
        vtn = VTNOps(base_url=base_url, auth_url=auth_url, client_id=client_id, client_secret=client_secret, auth_token_url_is_json=False )
        #print(vtn)
       # print(f"auth_token_url_is_json: {vtn.auth_token_url_is_json}")
        
        #ven = vtn.create_ven(resources=[Resource()])
        # Try creating a VEN without resources first
        ven = vtn.create_ven()
        
        vtn.get_programs()
        program = vtn.get_program('program-0')
      #  print(program)
        events = vtn.get_events()
        for event in events:
            reportDescriptor = event.getReportPayloadDescriptors()
            if reportDescriptor:
                vtn.send_report(event.getId(), program.getId(), ven, reportDescriptor)

        timeSeries = events.getTimeSeries()
        scheduler=EventScheduler()
        scheduler.setTimeSeries(timeSeries)
        scheduler.registerCallback(scheduler_callback)
        scheduler.registerFutureCallback(scheduler_future_callback, 30)
        scheduler.start()
        scheduler.join()
    except Exception as ex:
        oadr3_log_critical("main failed")


if __name__ == "__main__":
    main(None, None, None, None, None)