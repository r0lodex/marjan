import json
import os
from chalice import Chalice, Cron
from chalicelib.Email import Email
from chalicelib.Geotab import Geotab
from chalice.app import CloudWatchEvent

app = Chalice(app_name='geotab')

@app.schedule(Cron(0, 6, "*", "*", "MON-FRI", "*"))
def notify(event: CloudWatchEvent):
    recepients = os.environ.get("RECIPIENTS")
    notify = Email.send(
        "Geotab Daily Process Notification",
        "Data sent to {}: <br><br>{}".format(Geotab.RECEIVER_IP, Geotab.getLog()),
        recepients.split(",")
    )

    return notify

@app.schedule(Cron("1/5", "8-22", "?", "*", "MON-FRI", "*"))
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

            s = sock.sendto(bytes(d, "ascii"), (ip, port))

            result.append(d + ",socket_response: {}".format(s))

            print("Send result: {}".format(s))

    print("Logging to S3")
    Geotab.logResult(result)

    return result
