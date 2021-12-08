import json
import os
from chalice import Chalice, Cron
from chalicelib.Email import Email
from chalicelib.Geotab import Geotab
from chalice.app import CloudWatchEvent

app = Chalice(app_name='geotab')

@app.schedule(Cron(0, 6, "*", "*", "?", "*"))
def notify(event: CloudWatchEvent):

    notify = Email.send(
        "Geotab Daily Process Notification",
        "Data sent to {}: <br><br>{}".format(Geotab.RECEIVER_IP, Geotab.getLog()),
        os.environ.get("RECIPIENTS")
    )

    return notify

@app.schedule(Cron(0, 6, "*", "*", "?", "*"))
def send(event: CloudWatchEvent):
    Geotab.connect()
    devices = Geotab.getDevices()
    ip      = Geotab.RECEIVER_IP
    port    = Geotab.RECEIVER_PORT
    sock    = Geotab.SOCKET
    prefix  = Geotab.PREFIX

    result = []

    for dd in devices:
        status        = Geotab.getDeviceStatusInfo(dd["id"])
        ignitionData  = Geotab.getDeviceStatusData(dd["id"], "DiagnosticIgnitionId")
        gpsStatusData = Geotab.getDeviceStatusData(dd["id"], "DiagnosticPositionValidAtDeviceId")

        for i in status:
            print("Processing {}".format(dd["name"]))
            d = "{prefix},{vehicle_id},{event_code},{date},{time},{lat},{long},{speed},{heading},{gps_validity},{engine_bit}".format(
                prefix=prefix,
                vehicle_id=i["device"]["id"],
                event_code="02",
                date=Geotab.utc_to_local(i["dateTime"]).strftime("%d%m%Y"),
                time=Geotab.utc_to_local(i["dateTime"]).strftime("%H%M%S"),
                lat=i["latitude"],
                long=i["longitude"],
                speed=i["speed"],
                heading=i["bearing"],
                gps_validity="V" if gpsStatusData[0]["data"] < 1 else "A",
                engine_bit="01" if ignitionData[0]["data"] < 1 else "02"
            )

            result.append(d)

            s = sock.sendto(bytes(d, "ascii"), (ip, port))
            print("Send result: {}".format(s))

    print("Logging to S3")
    Geotab.logResult(result)

    return result
