# Download the helper library from https://www.twilio.com/docs/python/install
from twilio.rest import Client
from colortovision import * 


# Your Account Sid and Auth Token from twilio.com/console
# DANGER! This is insecure. See http://twil.io/secure
account_sid = TWILIO_ACCOUNT_SID;
auth_token = TWILIO_AUTH_TOKEN;

client = Client(account_sid, auth_token)

message = client.messages \
                .create(
                     body="Join Earth's mightiest heroes. Like Kevin Bacon.",
                     from_='+12562420018',
                     to='+16505217155'
                 )

print(message.sid)
