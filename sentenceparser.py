#!/usr/bin/env python

from watson_developer_cloud import AlchemyLanguageV1
import json


alchemy_language = AlchemyLanguageV1(api_key='35dd6afd583e326e6d8913597cbd7ce43d76cb6c')

def parse_sentence(sentence):
    try:
        response = alchemy_language.relations(text=sentence)
        #print response
        return response['relations'][0]
    except:
        return None

