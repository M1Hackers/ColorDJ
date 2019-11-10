"""Main server script for ColorDJ."""
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
        with open('{}/{}'.format("./images", filename), 'wb') as f:
            image_url = request.values['MediaUrl0']
            f.write(requests.get(image_url).content)

        resp.message("Thanks for the image!")
        filepath = "./images/" + filename
        image_attr = get_image_attributes(filepath)
        song_ids = get_playlist_ids(image_attr)

        playlist_link = make_playlist(
            filepath, image_attr["labels"].most_common(1)[0][0], song_ids)

        print(playlist_link)
        resp.message("spotify playlist link is " + playlist_link)
    else:
        resp.message("Try sending a picture message.")

    return str(resp)


if __name__ == "__main__":
    app.run(debug=True)
