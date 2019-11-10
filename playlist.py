import spotipy
import os
import random
import requests
import json
import base64
from PIL import Image

username = '6zqf0q9qifvh19a2wyub582ms'

import spotipy.util as util

def retrieve_client_info():
    f = open("spotify_key.txt")
    g = f.readlines()
    return g[0][:-1], g[1][:-1]

def retrieve_spotify_token():
    client_id, client_secret = retrieve_client_info()
    # print(client_id, client_secret)
    token = util.prompt_for_user_token(username, scope='playlist-modify-private,playlist-modify-public', client_id=client_id, client_secret=client_secret, redirect_uri='https://localhost:8080')
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
def make_playlist(filename, main_label, tracks):
    filename = filename.split(".")
    token = retrieve_spotify_token()
    sp = spotipy.Spotify(auth=token)
    # sp = spotipy.Spotify(auth=retrieve_already_token())

    r = random.randint(0,1000)
    playlist = sp.user_playlist_create(username, main_label + "_" + str(r))
    sp.user_playlist_add_tracks(username, playlist["id"], tracks)
    return playlist["external_urls"]['spotify']

    # resize the image and encode
    basewidth = 300
    img = Image.open(filename)
    wpercent = (basewidth/float(img.size[0]))
    hsize = int((float(img.size[1])*float(wpercent)))
    img = img.resize((basewidth,hsize), Image.ANTIALIAS)
    img.save(filename) 

    jpg_text_encoded = 'jpg1_b64 = \\\n"""' + base64.encodestring(open(filename,"rb").read()) + '"""'

    # add original image as playlist cover image
    endpoint_url = "https://api.spotify.com/v1/playlists/{playlist_id}/images"
    request_body = json.dumps({
        "playlist_id": playlist["id"],
        "Content-Type": jpg_text_encoded,
        "public": False,
    })

    response = requests.put(url = endpoint_url, data = request_body, headers={"Content-Type":"application/json", 
                            "Authorization":f"Bearer {token}"})
    print(response.status_code)


if __name__ == "__main__":
    url = make_playlist("bright", "", ['6DCZcSspjsKoFjzjrWoCdn', '6V1bu6o1Yo5ZXnsCJU8Ovk', '76cy1WJvNGJTj78UqeA5zr', '1rfofaqEpACxVEHIZBJe6W', '3swc6WTsr7rl9DqQKQA55C'])
    print(url)
