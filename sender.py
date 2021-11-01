import os
import pytz
import socket
from datetime import date, timedelta
from mygeotab import API as gtabApi
from dotenv import load_dotenv

load_dotenv()

client = gtabApi(
    username=os.environ.get("GEOTAB_USER"),
    password=os.environ.get("GEOTAB_PASS"),
    database=os.environ.get("GEOTAB_DB")
)

client.authenticate()

local_tz = pytz.timezone('Asia/Singapore')
lastVersions = [False, False, False]
startDate = date.today() - timedelta(10)

# Get all devices first
devices = client.get("Device")


def getDeviceStatusInfo(id):
    return client.call("Get", typeName="DeviceStatusInfo", search={"deviceSearch": {"id": id}})


def getDeviceStatusData(id, diagnosticId):
    return client.call("Get",
        typeName="StatusData",
        search={
            "toDate": date.today(),
            "deviceSearch": {"id": id},
            "diagnosticSearch": {"id": diagnosticId}
        }
    )


def utc_to_local(utc_dt):
    local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
    return local_tz.normalize(local_dt)


ip = os.environ.get("RECEIVER_IP")
port = int(os.environ.get("RECEIVER_PORT"))
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

for dd in devices:
    status = getDeviceStatusInfo(dd["id"])
    ignitionData = getDeviceStatusData(dd["id"], "DiagnosticIgnitionId")
    gpsStatusData = getDeviceStatusData(dd["id"], "DiagnosticPositionValidAtDeviceId")

    for i in status:
        print("Payload for {}:".format(dd["name"]))
        d = "{prefix},{vehicle_id},{event_code},{date},{time},{lat},{long},{speed},{heading},{gps_validity},{engine_bit}".format(
            prefix="VSL",
            vehicle_id=i["device"]["id"],
            event_code="02",
            date=utc_to_local(i["dateTime"]).strftime("%d%m%Y"),
            time=utc_to_local(i["dateTime"]).strftime("%H%M%S"),
            lat=i["latitude"],
            long=i["longitude"],
            speed=i["speed"],
            heading=i["bearing"],
            gps_validity="V" if gpsStatusData[0]["data"] < 1 else "A",
            engine_bit="01" if ignitionData[0]["data"] < 1 else "02"
        )

        res = sock.sendto(bytes(d, "ascii"), (ip, port))
        print(d)
