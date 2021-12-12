# MARJAN

A service that taps into GeoTab SDK and sends fleets' GPS data to MPOB

```bash
- pip install -r requirements.txt
- chalice deploy --stage x --profile "<aws profile if any otherwise ditch profile>"
```

### Raw Requirements

This requirement is taken directly from email

### Immediate Goals:

- To provide live (5 minute interval) GPS data of vehicles belong to MPOB members into MPOB servers
- GPS data need to be send to a fixed IP address, via UDP protocol and following data format set by MPOB (see attached Connectivity test GPS Panel-VSIM doc)

### Possible Method

- Collect GPS data from Geotab GO devices connected to MPOB members’ vehicles.
- Data can be collected / received via Geotab API/ using Geotab SDK
    - https://geotab.github.io/sdk/
    - https://www.geotab.com/tag/apis/

- Data to be interpreted and send to third party systems (MPOB server) based on data format set by MPOB
- Once testing is completed, data from vehicles need to be send in near-real time (5 minutes interval) to the MPOB server on daily basis -
- Data format shall be in ascli format (text file)
- GPS device shall provide the GPS information as below:
    - GPS Device Unit ID
    - GPS Date in UTC
    - GPS Time in UTC
    - GPS Coordinate: Latitude
    - GPS Heading/direction
    -  GPS Speed
    - GPS Data Life Span (Fresh or Last Known location data)
- Device Event Status:
    - Device Information of associated truck
    - Vehicle Plate Number
    - Device Model
    - Device Unit ID
    - Sim card number
    - Telco Provider

---

```
# SPS GPS Data Definitions

- IP Address: FROM_ENV
- Port: FROM_ENV
- Protocol: UDP
- Interval: 1 Minute
- Prefix: VSL
- Company Name: FROM_ENV

211.25.234.139> VSL,730,07,17032015,102837,1.46715,101.69373,110,180,A,02
211.25.234.139> VSL,730,07,17032015,102925,1.46715,101.69373,110,180,A,02

Position 1 (VSL) = Prefix √
Position 2 (730) = Unit ID (vehicle id) √
Position 3 (07) = Event Code (See Appendix I for more info) DeviceStatusInfo
Position 4 (17032015) = Date √
Position 5 (102837) = Time √
Position 6 (1.4671) = Latitude √
Position 7 (101.69373) = Longitude √
Position 8 (110) = Speed (kph) √
Position 9 (180) = Heading √
Position 10 (A) = GPS Validity (A=Good, V=Bad Gps) StatusData->DiagnosticPositionValidAtDeviceId [0 or 1]
Position 11(02) = Engine Bit (see Appendix II for more info) StatusData->DiagnosticIgnitionId

---

## Appendix I
### Event Codes

- 02 = Alarm
- 03 = Immo on
- 04 = Immo Off
- 07 = Speeding
- 10 = Time (Regular Tracking interval, normal status)
- 12 = Idling
- 23 = Beacon (Sleep Mode, Once every hour after engine off)

## Appendix II
### Engine Bit Codes

- 01 = Engine is off
- 02 = Engine is on
```

## Reference

```python
"""
DeviceStatusInfo
[
    {
        'bearing': -1,
        'currentStateDuration': datetime.time(1, 45, 43),
        'exceptionEvents': [
            {
                'activeFrom': datetime.datetime(2021, 4, 16, 4, 33, 39, tzinfo=datetime.timezone.utc),
                'activeTo': datetime.datetime(2021, 4, 16, 4, 33, 39, tzinfo=datetime.timezone.utc),
                'distance': 0.0, 'duration': datetime.time(0, 0),
                'rule': {
                    'id': 'acUHZ03Qok0i8J8LGsfA5YQ'
                },
                'device': {
                    'id': 'b2'
                },
                'diagnostic': 'NoDiagnosticId',
                'driver': 'UnknownDriverId',
                'version': '0000000000015cc1',
                'id': 'aR7fV17jjoESCi_Std_DD8A'
            }
        ],
        'isDeviceCommunicating': False,
        'isDriving': False,
        'latitude': 1.62455034,
        'longitude': 103.671577,
        'speed': 0.0,
        'dateTime': datetime.datetime(2021, 4, 16, 6, 19, 22, 63000, tzinfo=datetime.timezone.utc),
        'device': {
            'id': 'b2'
        },
        'driver': 'UnknownDriverId',
        'isHistoricLastDriver': True,
        'groups': [{'children': [], 'id': 'b2796'}]
    }
]
"""



calls = [
    [
        "Get", {
            "typeName":"Device"
        }
    ],

    # ["GetFeed", {"typeName":"StatusData" }],
    # ["GetFeed", {"typeName":"FaultData" }],
]

# devices = client.multi_call(calls)

# print(devices)
```