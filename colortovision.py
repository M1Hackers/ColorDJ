import os
import io
import colorsys

from google.cloud import vision
from google.cloud.vision import types
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types as language_types

import pandas as pd
import numpy as np
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "ColorDJ-12658b766abb.json"

def get_image_attributes(song_file):
	client = vision.ImageAnnotatorClient()
	language_client = language.LanguageServiceClient()

	file_name = os.path.abspath(song_file)

	# Loads the image into memory
	with io.open(file_name, 'rb') as image_file:
		content = image_file.read()

	image = types.Image(content=content)

	# Performs label detection on the image file
	label_response = client.label_detection(image=image)
	labels = label_response.label_annotations

	#Performs color detection on the image file
	color_response = client.image_properties(image=image)
	color_props = color_response.image_properties_annotation
	# print('Properties:')

	saturation = 0
	lightness = 0
	total_weight = 0
	sorted_colors = sorted(color_props.dominant_colors.colors, key=lambda color:color.score, reverse=True)
	for color in sorted_colors[:5]:
		h, l ,s = colorsys.rgb_to_hls(color.color.red/255, color.color.green/255, color.color.blue/255)
		saturation += color.score * s
		lightness += color.score * l
		total_weight += color.score

	color_dict = {}
	saturation = saturation / total_weight
	lightness = lightness / total_weight
	# print("Saturated: ", saturation)
	# print("Light: ", lightness)
	# print("total:weight: ", total_weight)

	sentiment_text = ""
	for label in labels:
		sentiment_text += label.description + " "

	document = language_types.Document(
		content=sentiment_text[:-1],
		type=enums.Document.Type.PLAIN_TEXT)

	# Detects the sentiment of the text
	sentiment = language_client.analyze_sentiment(document=document).document_sentiment

	sentiment_score = sentiment.score
	sentiment_mag = sentiment.magnitude

	return {"saturation":saturation, "lightness":lightness, "sentiment_score":sentiment_score, "sentiment_mag":sentiment_mag}

# song_attributes dictionary:
# "saturation" : (float) saturation value of an image [0,1]
# "lightness" : (float) lightness value of an image [0,1]
# "sentiment_score": (float) sentiment value of an image [-1,1]
# "sentiment_mag" : (float) sentiment magnitude (how strong the emos are) of an image [0, inf]
def get_playlist_ids(song_attributes):
	top2018 = pd.read_csv("data/top2018.csv")
	force_mode = 1 if song_attributes["sentiment_score"] >= 0 else 0
	similarity_euclid = {}
	for index, row in top2018.iterrows():
		danceability = float(row["danceability"])
		valence = float(row["valence"])
		energy = float(row["energy"])
		if force_mode != row["mode"]:
			continue
		similarity_euclid[row["id"]] = ((danceability - song_attributes["saturation"])**2 + (valence - song_attributes["lightness"]) ** 2 + (song_attributes["sentiment_mag"] - energy) ** 2) ** 0.5

	sorted_sims = sorted(similarity_euclid.items(), key=lambda kv: kv[1])

	playlist = [song[0] for song in sorted_sims[:10]]

	# for index, row in top2018.iterrows():
	# 	if row["id"] in playlist:
	# 		print(row["name"])
	return playlist

def words_contained(words, text):
    # return #words in words an text / # words in words
    set_words = set(words)
    if len(set_words) == 0:
        return 0
    else:
        return len(set_words.intersection(set(text.split()))) / len(set_words)

if __name__ == "__main__":
    image_attr = get_image_attributes("data/bright.jpg")
    playlist = get_playlist_ids(image_attr)
    print(playlist)
    print(get_lyrics("God's Plan", "Drake"))
