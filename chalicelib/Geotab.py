import os, pytz, socket, boto3
from botocore.exceptions import ClientError
from datetime import date, timedelta
from mygeotab import API as gtabApi
from dotenv import load_dotenv

load_dotenv()

class Geotab:
    PREFIX                     = os.environ.get("PREFIX")
    RECEIVER_IP                = os.environ.get("RECEIVER_IP")
    LOG_BUCKET                 = os.environ.get("LOG_BUCKET")
    RECEIVER_PORT              = int(os.environ.get("RECEIVER_PORT"))
    DIAGNOSTIC_IGNITION_ID     = "DiagnosticIgnitionId"
    DIAGNOSTIC_DEVICE_POSITION = "DiagnosticPositionValidAtDeviceId"
    SOCKET                     = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    LOG_FILE                   = date.today().strftime("%d-%m-%Y") + ".csv"

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
    def getDevices(self):
        return self.client.get("Device")

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

    @classmethod
    def logResult(self, result:list):
        s3 = boto3.client("s3")
        key = self.LOG_FILE
        content = ",".join(result) + ",*****\n"

        try:
            file = s3.get_object(Bucket=self.LOG_BUCKET, Key=key)
            old_content = file['Body'].read()
            content = old_content.decode("utf-8") + content
        except ClientError as ce:
            # Create a new file
            if ce.response["Error"]["Code"] == "NoSuchKey":
                print("{} does not exist. Creating...".format(key))
        except Exception as ex:
            print(ex)

        s3.put_object(Bucket=self.LOG_BUCKET, Key=key, Body=content)

    @classmethod
    def getLog(self):
        s3        = boto3.client("s3")
        today     = date.today()
        yesterday = today - timedelta(days=1)
        key       = yesterday.strftime("%d-%m-%Y") + ".csv"
        result    = "Error"

        try:
            file   = s3.get_object(Bucket=self.LOG_BUCKET, Key=key)
            result = file['Body'].read().decode("utf-8")
        except Exception as ex:
            print(ex)

        return result