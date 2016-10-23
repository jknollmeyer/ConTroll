#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json
import re


#returns a list of the key phrases in a document.
#tweet is a string
def getKeyPhrases(tweet):
    endpoint = "https://westus.api.cognitive.microsoft.com/text/analytics/v2.0/keyPhrases"
    headers = {'Ocp-Apim-Subscription-Key': '4c28d3a67a12442cad6666a3200c49f5', 'Content-Type': 'application/json', 'Accept': 'application/json'}
    
    json_stuff = {"documents": [{"language": "en", "id": "1", "text": tweet}]}

    r = requests.post(endpoint, headers=headers, json=json_stuff)

    keyPhrases = json.loads(r.text)['documents'][0][u'keyPhrases']
    keyPhrases = [x.encode('utf8') for x in keyPhrases]
    return keyPhrases
