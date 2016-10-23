#!/usr/bin/env python

from SentimentAnalysis import *
from keyphrases import *
from sentenceparser import *

import base64

DEBUG = False

#open the list of bad words
bad_phrases = base64.b64decode(open("badwordlist_b64", "r").read()).lower()
bad_phrases = bad_phrases.split('\n')

bad_phrase_table = {}
for phrase in bad_phrases:
    bad_phrase_table[phrase] = 1


#determines if a tweet should be considered a troll, based 
#on the sentiment of the tweet, and its vulgarity
def is_tweet_troll(tweet):
    tweet = tweet.lower()

    vulgarity_threshold = 0.35

    sentiment = getSentiment(tweet)
    troll_sentiment = 1 - sentiment
    #think of something to do with the key phrases

    bad_phrase_count = sum([len(phrase) for phrase in bad_phrase_table if phrase in tweet])
    

    #metrics: frequency of vulgar/blacklisted phrases
    #         sentiment level
    bad_phrase_ratio = (1.0 * bad_phrase_count/len(tweet))

    sentence_contents = parse_sentence(tweet)

    if DEBUG:
        print "tweet:", tweet
        print "troll_sentiment:", troll_sentiment
        print "bad_phrase_ratio", bad_phrase_ratio
        print "ratio * troll_sentiment", bad_phrase_ratio * troll_sentiment
        print "sentence contents", sentence_contents


    subject = ""
    if sentence_contents != None:
        subject = sentence_contents['subject']['text'].encode('utf8').lower()

    if subject == "you" or "your" in subject:
        if troll_sentiment > 0.5:
            return True

    #make sure that there's at least some blacklisted words
    #otherwise low sentiment could cause a false positive.
    if bad_phrase_ratio > vulgarity_threshold:
        if bad_phrase_ratio * troll_sentiment > 0.2:
            return True
        
    return False
