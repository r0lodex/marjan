import os, pytz, socket
from datetime import date
from mygeotab import API as gtabApi
from dotenv import load_dotenv

load_dotenv()

class Geotab:
    PREFIX                     = os.environ.get("PREFIX")
    RECEIVER_IP                = os.environ.get("RECEIVER_IP")
    RECEIVER_PORT              = int(os.environ.get("RECEIVER_PORT"))
    DIAGNOSTIC_IGNITION_ID     = "DiagnosticIgnitionId"
    DIAGNOSTIC_DEVICE_POSITION = "DiagnosticPositionValidAtDeviceId"
    SOCKET                     = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    @classmethod
    def connect(self):
        self.client = gtabApi(
            username=os.environ.get("GEOTAB_USER"),
            password=os.environ.get("GEOTAB_PASS"),
            database=os.environ.get("GEOTAB_DB")
        )

        self.client.authenticate()

        return self.client

    @classmethod
    def getDeviceStatusInfo(self, id):
        return self.client.call("Get", typeName="DeviceStatusInfo", search={"deviceSearch": {"id": id}})

    @classmethod
    def getDeviceStatusData(self, id, diagnosticId):
        return self.client.call("Get",
            typeName="StatusData",
            search={
                "toDate": date.today(),
                "deviceSearch": {"id": id},
                "diagnosticSearch": {"id": diagnosticId}
            }
        )

    @classmethod
    def utc_to_local(self, utc_dt):
        local_tz = pytz.timezone('Asia/Singapore')
        local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
        return local_tz.normalize(local_dt)