from collections import Counter
import colorsys
import os
import pickle

import colour
from google.cloud import vision
from google.cloud.vision import types
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types as language_types
import pandas
import numpy

import random

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "ColorDJ-c6da10562c7b.json"


def get_image_attributes(image_bytes):
    client = vision.ImageAnnotatorClient()
    language_client = language.LanguageServiceClient()
    image = types.Image(content=image_bytes)

    # Performs label detection on the image file.
    label_response = client.label_detection(image=image)
    labels = label_response.label_annotations

    object_response = client.object_localization(image=image)
	
	# objects
    object_annotations = object_response.localized_object_annotations
    object_names = [obj.name for obj in object_annotations]
    title = labels[0].description
    if len(object_names) > 0:
        title = object_names[0]
        label_names = [l.description.lower() for l in labels]
        for object_name in object_names:
    	    if object_name.lower() in label_names:
    		    title = object_name
    		    break

    # Performs color detection on the image file.
    color_response = client.image_properties(image=image)
    color_props = color_response.image_properties_annotation

    # Performs face / feeling detection on the image file
    face_response = client.face_detection(image=image)
    faces = face_response.face_annotations
    # Names of likelihood from google.cloud.vision.enums
    likelihood_name = ('UNKNOWN', 'VERY_UNLIKELY', 'UNLIKELY', 'POSSIBLE',
                       'LIKELY', 'VERY_LIKELY')
    joy = 0
    anger = 0
    sorrow = 0
    for face in faces:
        if ((face.anger_likelihood == 4) | (face.anger_likelihood == 5) | (face.anger_likelihood == 3)):
            anger += 1
        if ((face.joy_likelihood == 4) | (face.joy_likelihood == 5) | (face.joy_likelihood == 3)):
            joy += 1
        if ((face.sorrow_likelihood == 4) | (face.sorrow_likelihood == 5) | (face.sorrow_likelihood == 3)):
            sorrow += 1
    print([["pos", joy], ["neg", anger], ["neg", sorrow]])
    emotion = max([["pos", joy], ["neg", anger], ["neg", sorrow]], key = lambda x: x[1])[0]
    # print(emotion)

    saturation = 0
    lightness = 0
    temperature = 0
    total_weight = 0
    sorted_colors = sorted(color_props.dominant_colors.colors,
                           key=lambda color: color.score, reverse=True)
    for color in sorted_colors[:5]:
        h, l, s = colorsys.rgb_to_hls(color.color.red/255, color.color.green/255, color.color.blue/255)
        saturation += color.score * s
        lightness += color.score * l
        t = color_to_temperature(color.color)
        if 1000 <= t <= 16000:
            temperature += color.score * (t - 1000) / 15000
        total_weight += color.score

    saturation = saturation / total_weight
    lightness = lightness / total_weight
    temperature = temperature / total_weight

    sentiment_text = " ".join(label.description for label in labels)

    document = language_types.Document(
        content=sentiment_text,
        type=enums.Document.Type.PLAIN_TEXT)

    # Detects the sentiment of the text
    sentiment = language_client.analyze_sentiment(document=document).document_sentiment

    sentiment_score = sentiment.score
    sentiment_mag = sentiment.magnitude

    return {
        "saturation": saturation,
        "lightness": lightness,
        "sentiment_score": sentiment_score,
        "sentiment_mag": sentiment_mag,
        "labels": Counter({label.description.lower(): label.score for label in labels}),
        "temp_score": 1 - temperature,
        "feelings": emotion,
		"title": title
    }


def get_playlist_ids(song_attributes):
    """
    Arguments:
        song_attributes (dict):
            "saturation" : (float) saturation value of an image [0,1]
            "lightness" : (float) lightness value of an image [0,1]
            "sentiment_score": (float) sentiment value of an image [-1,1]
            "sentiment_mag" : (float) sentiment magnitude of an image [0, inf]
            "labels" : (dict) labels in image
            "temperature" : (float) temperature of image
            "feelings" : (string) "pos" or "neg", facial emotions in the image
    """
    top = pandas.read_csv("data/top2005_2017.csv")
    with open("data/top2005_2017_lyrics_wordfreqs.pkl", "rb") as f:
        top_lyrics = pickle.load(f)
    force_mode = 1 if song_attributes["sentiment_score"] >= 0 else 0
    print(song_attributes["temp_score"])
    distance = {}
    for index, row in top.iterrows():
        danceability = float(row["danceability"])
        valence = float(row["valence"])
        energy = float(row["energy"])
        liveness = float(row["liveness"])
        if force_mode != row["mode"]:
            continue
        keyword_freqs = top_lyrics.get(row["id"], Counter())
        word_score = 1
        for kw in keyword_freqs & song_attributes["labels"]:
            word_score *= 1 - keyword_freqs[kw]
            word_score *= 1 - song_attributes["labels"][kw]
        color_distance = (
            (danceability - song_attributes["saturation"])**2
            + (valence - song_attributes["lightness"]) ** 2
            + (energy - song_attributes["sentiment_mag"]) ** 2
            + (liveness - song_attributes["temp_score"]) ** 2) ** 0.5
        distance[row["id"]] = color_distance * word_score

    sorted_sims = sorted(distance.items(), key=lambda kv: kv[1])

    playlist = [song[0] for song in sorted_sims[:5]]
    ## add five songs randomly by emotion
    print(song_attributes["feelings"])
    songs_by_feelings = []
    if (song_attributes["feelings"] == "pos"):
        df = pandas.read_csv("data/songs_by_sentiment_pos.csv")
        songs_by_feelings = random.sample(df.values.tolist(), 5)
    else:
        df = pandas.read_csv("data/songs_by_sentiment_neg.csv")
        songs_by_feelings = random.sample(df.values.tolist(), 5)

    # print(songs_by_feelings)
    for song in songs_by_feelings:
        playlist.append(song[1])

    return playlist


def words_contained(words, text):
    # return #words in words an text / # words in words
    set_words = set(words)
    if len(set_words) == 0 or text is None:
        return 0
    else:
        return len(set_words.intersection(set(text.split()))) / len(set_words)


def color_to_temperature(color):
    xyz = colour.sRGB_to_XYZ(
        numpy.array([color.red, color.green, color.blue]) / 255)
    return colour.xy_to_CCT(colour.XYZ_to_xy(xyz), 'hernandez1999')




if __name__ == "__main__":
    image_attr = get_image_attributes("data/upset.jpg")
    playlist = get_playlist_ids(image_attr)
    print(playlist)
