import json
import uuid
from .log import Oadr3LoggedException, oadr3_log_critical
from .config import OADR3Config
from .definitions import oadr3_report_types, oadr3_report_reading_types

class Resource(dict):
    def __init__(self, json_data=None, name=None):
        try:
            if json_data:
                super().__init__(json_data)
                # Ensure 'id' exists
                if "id" not in self or self["id"] is None:
                    self["id"] = str(uuid.uuid4())
            else:
                # Initialize default fields
                super().__init__({
                    "id": str(uuid.uuid4()),  # Generate unique ID
                    "resourceName": name if name else OADR3Config.default_system_resource_name,
                    "attributes": [],
                    "targets": [],
                    "objectType": "RESOURCE"
                })
        except Exception as ex:
            raise Oadr3LoggedException('critical', "exception in Resource Init-json", True)

    def setName(self, name:str):
        if not name:
            return
        self['resourceName'] = name

    def getReportPayload(self, programId, eventId, venName=OADR3Config.default_client_name):
        try:
            resourceName = self['resourceName']
            return json.dumps({
                "programID": f"{programId}",
                "eventID": f"{eventId}",
                "clientName": f"{venName}",
                "resources": [
                    {
                        "resourceName": f"{resourceName}",
                        "intervals": [
                            {
                                "id": "resource-1",
                                "payloads": [
                                    {
                                        "type": f"{OADR3Config.default_system_resource_type}",
                                        "values": [
                                            "NORMAL"
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                ]
            })
        except Exception as ex:
            oadr3_log_critical("couldn't create report payload")
            return None