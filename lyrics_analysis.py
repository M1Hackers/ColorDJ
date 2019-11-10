from collections import Counter
import pickle
import re
import sys

import pandas
from textblob import TextBlob


def lyrics_keyword_freqs(source):
    """Calculate word frequencies for songs.

    Arguments:
        source (pandas.DataFrame): a data frame with id and lyrics columns

    Returns:
        dict: mapping from song ids to Counters containing word frequencies

    """
    word_freq = {}
    for song in source.itertuples():
        lyrics = song.lyrics
        if type(lyrics) is not str:
            continue
        lyrics = re.sub(r"\[.+\]", "", lyrics)  # remove annotations
        tb = TextBlob(song.lyrics)
        wc = tb.word_counts
        wc_normalized = {w: (c / max(wc.values())) for w, c in wc.items()}
        word_freq[song.id] = Counter(wc_normalized)
    return word_freq


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("No filename provided")
        exit()
    fname = sys.argv[1].rsplit(".", 1)[0]
    all_songs = pandas.read_csv(fname + ".csv")
    kwf = lyrics_keyword_freqs(all_songs)
    with open(fname + "_wordfreqs.pkl", "xb") as f:
        pickle.dump(kwf, f)
