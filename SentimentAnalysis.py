#!/usr/bin/env python

"""
Sentiment Analysis using the Microsoft GetSentiment single response API
"""

# -*- coding: utf-8 -*-

import requests as r
import urllib2 as u
import json as j

#Returns a value between 0 and 1. 0 is a wholly negative string, 
#and 1 is a wholly positive string
def getSentiment(s):
    """ Gets the sentiment of a string and returns the score."""
    headers = {"Ocp-Apim-Subscription-Key" : "4c28d3a67a12442cad6666a3200c49f5",
               "Content-Type" : "application/json", "Accept" : "application/json"}
    url = "https://westus.api.cognitive.microsoft.com/text/analytics/v2.0/sentiment"
    json = {"documents": [{"language": "en", "id" : "1"}]}
    json['documents'][0]['text'] = s
    sentiment = r.post(url, headers = headers, json = json)
    sentiment = j.loads(sentiment.text)
    return sentiment['documents'][0]['score']

