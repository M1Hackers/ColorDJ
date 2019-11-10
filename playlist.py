import spotipy
import os
import random
import requests
import json
import urllib2
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
    print(client_id, client_secret)
    token = util.prompt_for_user_token(username, scope='playlist-modify-private,playlist-modify-public', client_id=client_id, client_secret=client_secret, redirect_uri='https://localhost:8080')
    print("TOKEN: " , token)
    return token

def retrieve_already_token():
    f = open("spotify_key.txt")
    g = f.readlines()
    return g[2][:-1]

# playlist is a list of IDs
def make_playlist(filename, tracks):
    filename = filename.split(".")
    # sp = spotipy.Spotify(auth=retrieve_spotify_token())
    sp = spotipy.Spotify(auth=retrieve_already_token())

    r = random.randint(0,1000)
    playlist = sp.user_playlist_create(username, filename[0] + "_" + str(r))
    print(playlist)
    sp.user_playlist_add_tracks(username, playlist["id"], tracks)

    # resize the image
    basewidth = 300
    img = Image.open(filename)
    wpercent = (basewidth/float(img.size[0]))
    hsize = int((float(img.size[1])*float(wpercent)))
    img = img.resize((basewidth,hsize), Image.ANTIALIAS)
    img.save(filename) 
    # add original image as playlist cover image
    endpoint_url = "https://api.spotify.com/v1/playlists/{playlist_id}/images"

    request_body = json.dumps({
              "playlist_id": playlist["id"],
              "Content-Type": base64.urlencode
              "public": False
            })


    response = requests.post(url = endpoint_url, data = request_body, headers={"Content-Type":"application/json", 
                            "Authorization":f"Bearer {token}"})

    url = response.json()['external_urls']['spotify']
    print(response.status_code)

if __name__ == "__main__":
    make_playlist("bright.jpg", ['2xGjteMU3E1tkEPVFBO08', '1gm616Plq4ScqNi7TVkZ5', '0tgVpDi06FyKpA1z0VMD4', '63SevszngYpZOwf63o61K', '1bhUWB0zJMIKr9yVPrkEu', '7vGuf3Y35N4wmASOKLUVV', '5k38wzpLb15YgncyWdTZE', '5OCJzvD7sykQEKHH7qAC3', '3EPXxR3ImUwfayaurPi3c', '4eWQlBRaTjPPUlzacqEeo'])
