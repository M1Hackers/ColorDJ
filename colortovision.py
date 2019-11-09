import os
import io
import colorsys

from google.cloud import vision
from google.cloud.vision import types
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types as language_types

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "ColorDJ-12658b766abb.json"

client = vision.ImageAnnotatorClient()
language_client = language.LanguageServiceClient()

file_name = os.path.abspath('data/happy.jpg')

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
print('Properties:')

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
print("Saturated: ", saturation)
print("Light: ", lightness)
print("total:weight: ", total_weight)

sentiment_text = ""
print('Labels:')
for label in labels:
    sentiment_text += label.description + " "

document = language_types.Document(
    content=sentiment_text[:-1],
    type=enums.Document.Type.PLAIN_TEXT)

# Detects the sentiment of the text
sentiment = language_client.analyze_sentiment(document=document).document_sentiment

sentiment_score = sentiment.score
print('Text: {}'.format(sentiment_text[:-1]))
print('Sentiment: {}, {}'.format(sentiment.score, sentiment.magnitude))
