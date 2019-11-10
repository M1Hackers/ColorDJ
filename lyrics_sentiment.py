## take in the lyrics
## write out to CSV file with sentiment, and probability values 
## song_id | (pos/neg) | pos_prob | neg_prob

import pandas as pd 
from textblob import TextBlob
from textblob.sentiments import NaiveBayesAnalyzer


def get_song_feelings(song_id, song_lyric):
	# for each row / song, grab id and lyrics
	if not isinstance(song_lyric, float):
		song_sentiment = TextBlob(song_lyric, analyzer=NaiveBayesAnalyzer()).sentiment
		song_feeling = song_sentiment[0]
		
		add_song_to_sentiment_list(song_id, song_feeling)
		return song_feeling
	add_song_to_sentiment_list(song_id, "pos")
	return "pos"

def add_song_to_sentiment_list(song_id, song_feeling):
	songs_by_sentiment[song_feeling].append(song_id)


songs = pd.read_csv("data/top2005_2017_lyrics.csv")
songs_by_sentiment = {"pos": [], "neg": []}

songs["feelings"] = songs.apply(lambda row: get_song_feelings(row["id"], row["lyrics"]), axis=1)

## create a dict to csv file of song id's and their sentiment
print(songs_by_sentiment)
df_pos = pd.DataFrame(songs_by_sentiment["pos"])
df_neg = pd.DataFrame(songs_by_sentiment["neg"])

# print(df_pos)
# pritn(df_neg)
df_pos.to_csv("data/songs_by_sentiment_pos.csv")
df_neg.to_csv("data/songs_by_sentiment_neg.csv")
songs.to_csv("data/top2005_2017_lyrics_feelings.csv")

