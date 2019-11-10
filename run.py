# Download the twilio-python library from twilio.com/docs/libraries/python
# import colortovision
import requests
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import colortovision

app = Flask(__name__)

@app.route("/sms", methods=['GET', 'POST'])
def sms_ahoy_reply():
    """Respond to incoming messages with a friendly SMS."""

    resp = MessagingResponse()

    if request.values['NumMedia'] != '0':

        # Use the message SID as a filename.
        filename = request.values['MessageSid']+ '.png'
        with open('{}/{}'.format("./images", filename), 'wb') as f:
           image_url = request.values['MediaUrl0']
           f.write(requests.get(image_url).content)

        resp.message("Thanks for the image!")

        image_attr = get_image_attributes(f)
        playlist = get_playlist_ids(image_attr)
        print(playlist)
        resp.message("spotify playlist link" + playlist[0])
    else:
        resp.message("Try sending a picture message.")
    

    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)

