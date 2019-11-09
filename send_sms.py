# Download the helper library from https://www.twilio.com/docs/python/install
from twilio.rest import Client


# Your Account Sid and Auth Token from twilio.com/console
# DANGER! This is insecure. See http://twil.io/secure
account_sid = 'ACd6b06b47c7cd386c757ed492b50dea69'
auth_token = '83bb662d1c18a58c1c4fa12365115612'
client = Client(account_sid, auth_token)

message = client.messages \
                .create(
                     body="Join Earth's mightiest heroes. Like Kevin Bacon.",
                     from_='+12562420018',
                     to='+16505217155'
                 )

print(message.sid)
