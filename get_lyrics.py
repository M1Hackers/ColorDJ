import requests
import sys

from bs4 import BeautifulSoup
import pandas as pd

import config


def get_lyrics(song_title, artist_name):
    print(song_title)
    song_title = song_title.replace('?', '')
    artist_name = artist_name.replace('?', '')
    # https://github.com/willamesoares/lyrics-crawler

    base_url = 'https://api.genius.com'
    headers = {'Authorization': 'Bearer ' + config.genius_api_token}
    search_url = base_url + '/search'
    data = {'q': song_title + ' ' + artist_name}
    response = requests.get(search_url, data=data, headers=headers)
    json = response.json()
    remote_song_info = None

    for hit in json['response']['hits']:
        if artist_name.lower() in hit['result']['primary_artist']['name'].lower():
            remote_song_info = hit
            break
    if remote_song_info is None:
        # retry with only first word
        if len(song_title.split()) > 1:
            return get_lyrics(song_title.split()[0], artist_name)
        else:
            return None
    else:
        song_url = remote_song_info['result']['url']
        return scrap_song_url(song_url)


def scrap_song_url(url):
    # https://github.com/willamesoares/lyrics-crawler
    page = requests.get(url)
    html = BeautifulSoup(page.text, 'html.parser')
    [h.extract() for h in html('script')]
    lyrics = html.find('div', class_='lyrics').get_text()

    return lyrics


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("No filename provided")
        exit()
    fname = sys.argv[1].rsplit(".", 1)[0]
    songs = pd.read_csv(fname + ".csv")
    songs["lyrics"] = songs.apply(lambda row: get_lyrics(row["name"], row["artists"]), axis=1)
    songs.to_csv(fname + "_lyrics.csv")
