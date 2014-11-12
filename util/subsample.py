#!/usr/bin/env python
from DataStreamer import DataStreamer, Example
from collections import Counter
import os
import cPickle as pickle


"""Module for subsampling the data so that we only concern ourselves
with posts that have one of the 1000 most frequent tags.
"""

with open('../full_data/tags.count', 'rb') as f:
    counts = pickle.load(f)

keep_n = 1000

most_common = counts.most_common(keep_n)

most_common_tags = [tag for tag, count in most_common]

i=0
j=0
with open('subsample.examples.pickle', 'wb') as f:
    for example in DataStreamer.load_from_file('/tmp/Train.csv'):
        if i%10000 == 0:
            print 'processed', i, 'dumped', j
        tags = example.data['tags']
        matching = set(tags).intersection(most_common_tags)
        if len(matching):
            # match
            example.data['tags'] = list(matching)
            pickle.dump(example, f, protocol=pickle.HIGHEST_PROTOCOL)
            j += 1
        i += 1

print 'processed', i, 'dumped', j
    
