"""Main server script for ColorDJ."""
import os
import requests
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from colortovision import get_image_attributes, get_playlist_ids
from playlist import make_playlist

app = Flask(__name__)


@app.route("/sms", methods=['GET', 'POST'])
def sms_ahoy_reply():
    """Respond to incoming messages with a friendly SMS."""
    resp = MessagingResponse()

    if request.values['NumMedia'] != '0':

        # Use the message SID as a filename.
        filename = request.values['MessageSid'] + '.jpg'
        filepath = os.path.join(os.getcwd(), "images", filename)
        with open(filepath, 'wb') as f:
            image_url = request.values['MediaUrl0']
            f.write(requests.get(image_url).content)

        image_attr = get_image_attributes(filepath)
        song_ids = get_playlist_ids(image_attr)

        playlist_link = make_playlist(
            filepath, image_attr["title"].most_common(1)[0][0], song_ids)

        print(playlist_link)
        resp.message("Listen to your new playlist at " + playlist_link)
    else:
        resp.message("Try sending a picture message.")

    return str(resp)


if __name__ == "__main__":
    app.run(debug=True)
