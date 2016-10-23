#!/usr/bin/env python

from collections import Counter
import scipy.spatial


#list1 and list2 are lists of tweets (lists of strings)
#this function returns the cosine similarity of the two tweet lists.
def compare_tweets(list1, list2):

    #combine tweets into one string
    words1 = "".join(list1)
    words2 = "".join(list2)

    #replace punctuation
    words1.replace(".", "")
    words1.replace("?", "")
    words1.replace("!", "")
    words2.replace(".", "")
    words2.replace("?", "")
    words2.replace("!", "")

    counts_1 = Counter(words1.split(" "))
    counts_2 = Counter(words2.split(" "))

    words = list(set(counts_1) | set(counts_2))

    count_vect_1 = [counts_1.get(word, 0) for word in words]
    count_vect_2 = [counts_2.get(word, 0) for word in words] 

    similarity = 1 - scipy.spatial.distance.cosine(count_vect_1, count_vect_2)
    return similarity


if __name__ == '__main__':
    print("testing:")
    tweets1 = ["a b c d e f g", "j i d w n c", "f i s q m ", "e q p c i s n"]
    tweets2 = ["a b c d e f g", "j j d w n c"]
    print (compare_tweets(tweets1, tweets2))