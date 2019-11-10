import pandas as pandas
import requests
import spotipy.util as util
import numpy as np
import pandas as pd
PLAYLIST_ID = "2fQ59B3on45R3rgcfnKDbD"
username = '6zqf0q9qifvh19a2wyub582ms'

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

def scrape_playlist(playlist_id):
    token = retrieve_spotify_token()
    song_dict = {}

    for i in [0,100,200,300,400]:
        endpoint_url = "https://api.spotify.com/v1/playlists/" + playlist_id + "/tracks?fields=items(track(id))&offset=" + str(i)
        playlist_response = requests.get(endpoint_url, headers={"Authorization":"Bearer {}".format(token)})
        playlist_response = playlist_response.json()
        list_ids = [song['track']['id'] for song in playlist_response["items"]]
        # (danceability, energy, key, loudness, mode, speechiness, acousticness, instrumentalness, liveness, valence, tempo, durationms, time sig, pitch_var, weight_var)
        for song_id in list_ids:
            print(song_id)
            url = "https://api.spotify.com/v1/audio-features/" + song_id
            response = requests.get(url, headers={"Authorization":"Bearer {}".format(token)})
            response = response.json()
            analysis_url = "https://api.spotify.com/v1/audio-analysis/" + song_id
            analysis_response = requests.get(analysis_url, headers={"Authorization":"Bearer {}".format(token)})
            pitch_var = 8.0
            weight_var = 0.1
            if 'segments' in analysis_response.json():
                pitches = [song["pitches"] for song in analysis_response.json()['segments']]
                weights = [song["duration"] for song in analysis_response.json()['segments']]
                weight_var = np.var(weights)
                pitch_var = np.var([np.argmax(p) for p in pitches])
            features_tup = (str(response["danceability"]), str(response["energy"]), str(response["key"]), str(response["loudness"]), str(response["mode"]), str(response["speechiness"]), str(response["acousticness"]), str(response["instrumentalness"])
                                , str(response["liveness"]), str(response["valence"]), str(response["tempo"]), str(response["duration_ms"]), str(response["time_signature"]), str(pitch_var), str(weight_var))
            song_dict[song_id] = features_tup

    return song_dict



def write_playlist_to_csv(song_dict):
    """
    Arguments:
        song_attributes (dict):
            "saturation" : (float) saturation value of an image [0,1]
            "lightness" : (float) lightness value of an image [0,1]
            "sentiment_score": (float) sentiment value of an image [-1,1]
            "sentiment_mag" : (float) sentiment magnitude of an image [0, inf]
            "labels" : (list of string) labels in image
            "temperature" : (float) temperature of image
    """
    CSV = "\n".join([k+","+",".join(v) for k,v in song_dict.items()])
    with open("data/top2005_2017.csv", "w") as file:
        file.write(CSV)
    print("Success")

def get_artist_songname():
    songs = []
    artists = []
    top2018 = pd.read_csv("data/top2005_2017_new.csv")
    token = retrieve_spotify_token()
    for index, row in top2018.iterrows():
        song_id = row["id"]
        endpoint_url = "https://api.spotify.com/v1/tracks/" + song_id
        song_response = requests.get(endpoint_url, headers={"Authorization":"Bearer {}".format(token)})
        song_response = song_response.json()
        artist = song_response['artists'][0]["name"]
        song_name = song_response["name"]

        songs.append(song_name)
        artists.append(artist)
    top2018['name'] = songs
    top2018['artists'] = artists

    top2018.to_csv("data/top2005_2017_new.csv")

if __name__ == "__main__":
    # song_dict = scrape_playlist(PLAYLIST_ID)
    # write_playlist_to_csv(song_dict)
    get_artist_songname()
