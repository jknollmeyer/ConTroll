#!/usr/bin/env python

from SentimentAnalysis import *
from keyphrases import *
import base64

bad_phrases = base64.b64decode(open("badwordlist_b64", "r").read()).lower()
bad_phrases = bad_phrases.split('\n')

bad_phrase_table = {}
for phrase in bad_phrases:
    bad_phrase_table[phrase] = 1


def check_tweet_troll_levels(tweet):
    tweet = tweet.lower()
    sentiment_threshold = 0.5
    vular_ratio_ = 0.5

    tweet_word_count = len(tweet.split(' '))
    sentiment = getSentiment(tweet)
    #think of something to do with the key phrases

    bad_phrase_count = sum([1 for phrase in bad_phrase_table if phrase in tweet])
    

    #metrics: frequency of vulgar/blacklisted phrases
    #         sentiment leverl



    #if a large percent of the tweet is just vulgarity
    bad_phrase ratio = (bad_phrase_count/tweet_word_count)



if __name__ == '__main__':
    print ()