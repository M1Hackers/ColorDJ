import io
import spotipy
import os
import random
import requests
import json
import base64
from PIL import Image

username = '6zqf0q9qifvh19a2wyub582ms'

emojis = [':D', ':)', ':O',':/',"o.o",";_;", "XD", "T.T", ">:(", ":')", ":|", ";)"]

import spotipy.util as util

def retrieve_client_info():
    f = open("spotify_key.txt")
    g = f.readlines()
    return g[0][:-1], g[1][:-1]

def retrieve_spotify_token():
    client_id, client_secret = retrieve_client_info()
    # print(client_id, client_secret)
    token = util.prompt_for_user_token(username, scope='playlist-modify-private,playlist-modify-public,ugc-image-upload', client_id=client_id, client_secret=client_secret, redirect_uri='https://localhost:8080')
    # print("TOKEN: " , token)
    return token

def retrieve_already_token():
    f = open("spotify_key.txt")
    g = f.readlines()
    return g[2][:-1]

# FUNCTION YOU WANT TO CALL FROM MAIN 
# tracks is a list of IDs
# main_label is a string
# returns: URL of playlist
def make_playlist(image_bytes, main_label, tracks):
    token = retrieve_spotify_token()
    sp = spotipy.Spotify(auth=token)
    # sp = spotipy.Spotify(auth=retrieve_already_token())

    r = random.randint(0, len(emojis)) 
    print(emojis[r])
    playlist = sp.user_playlist_create(username, f"{main_label} {emojis[r]}")

    quote = requests.get("http://quotes.rest/qod.json").json()
    desc = "Perfection is not attainable, but if we chase perfection we can catch excellence... - Vince Lombardi"
    if 'contents' in quote.keys():
        desc_new = quote['contents']['quotes'][0]['quote'] + ' - ' + quote['contents']['quotes'][0]['author']
        desc = desc_new if len(desc_new) < 101 else desc

    print(desc)
    desc_json = json.dumps({"description": desc})
    endpoint_url_desc = "https://api.spotify.com/v1/playlists/" + playlist["id"]
    response_desc = requests.put(endpoint_url_desc, data=desc_json, headers={"Authorization":"Bearer {}".format(token), "Content-Type":"application/json"})


    sp.user_playlist_add_tracks(username, playlist["id"], tracks)

    # resize the image and encode
    basewidth = 300
    img = Image.open(io.BytesIO(image_bytes))
    wpercent = (basewidth/float(img.size[0]))
    hsize = int((float(img.size[1])*float(wpercent)))
    img = img.resize((basewidth, hsize), Image.ANTIALIAS)
    resized_image = io.BytesIO()
    img.save(resized_image, 'jpeg')
    resized_image.seek(0)
    jpg_text_encoded = base64.b64encode(resized_image.read())
    # add original image as playlist cover image
    endpoint_url = "https://api.spotify.com/v1/playlists/" + playlist["id"] + "/images"
    requests.put(endpoint_url, data=jpg_text_encoded, headers={"Authorization": "Bearer {}".format(token), "Content-Type": "image/jpeg"})
    return playlist["external_urls"]['spotify']


if __name__ == "__main__":
    url = make_playlist("data/bright.jpg", "bright", ['6DCZcSspjsKoFjzjrWoCdn', '6V1bu6o1Yo5ZXnsCJU8Ovk', '76cy1WJvNGJTj78UqeA5zr', '1rfofaqEpACxVEHIZBJe6W', '3swc6WTsr7rl9DqQKQA55C'])
    print(url)
