"""Main server script for ColorDJ."""
import io
import requests

from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

from colortovision import get_image_attributes, get_playlist_ids
from playlist import make_playlist


app = Flask(__name__)


@app.route("/sms", methods=['GET', 'POST'])
def songify_sms_image():
    """Respond to incoming images with the URL to a new Spotify playlist."""
    resp = MessagingResponse()

    if request.values['NumMedia'] != '0':
        # Download user image.
        image_url = request.values['MediaUrl0']
        image = requests.get(image_url).content

        # Analyze image using Cloud Vision API.
        image_attr = get_image_attributes(image)

        # Retrieve a list of relevant songs.
        song_ids = get_playlist_ids(image_attr)

        # Create a Spotify playlist.
        playlist_link = make_playlist(image, image_attr["title"], song_ids)

        resp.message("Listen to your new playlist at " + playlist_link)
    else:
        resp.message("Try sending a picture message.")

    return str(resp)


if __name__ == "__main__":
    app.run(debug=True)
