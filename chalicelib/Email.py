import boto3, os
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()

class Email:
    SENDER = os.environ.get("SENDER")
    CHARSET = "UTF-8"

    @classmethod
    def send(self, subject: str, message: str, recipients: list) -> dict:
        client = boto3.client('ses')
        body_html = "<html><head></head><body><code>{}</code></body></html>".format(message)

        try:
            #Provide the contents of the email.
            response = client.send_email(
                Destination={
                    'ToAddresses': recipients,
                },
                Message={
                    'Body': {
                        'Html': {
                            'Charset': self.CHARSET,
                            'Data': body_html,
                        },
                        'Text': {
                            'Charset': self.CHARSET,
                            'Data': message,
                        },
                    },
                    'Subject': {
                        'Charset': self.CHARSET,
                        'Data': subject,
                    },
                },
                Source=self.SENDER,
            )

        except ClientError as e:
            return e.response['Error']['Message']
        else:
            return response['MessageId']
