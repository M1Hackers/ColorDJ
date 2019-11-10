import requests
from bs4 import BeautifulSoup
import pandas as pd

def get_lyrics(song_title, artist_name):
    print(song_title)
    # https://github.com/willamesoares/lyrics-crawler
    token_file = open("genius_api_token.txt","r") 
    token = token_file.readline()[:-1]
    token_file.close() 

    base_url = 'https://api.genius.com'
    headers = {'Authorization': 'Bearer ' + token}
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


songs = pd.read_csv("data/top2018.csv")
songs["lyrics"] = songs.apply(lambda row: get_lyrics(row["name"], row["artists"]) , axis=1)

songs.to_csv("data/top2018_lyrics.csv")
