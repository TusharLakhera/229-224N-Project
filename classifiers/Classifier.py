#!/usr/bin/env python

"""Base classifier class from which all classifiers inherit.
Defines skeleton constructor, training, and prediction methods."""

import ast
import sys
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import f1_score
import numpy as np
from scipy.sparse import csr_matrix
sys.path.append("../features")
import common
sys.path.append("../util")
from DataStreamer import DataStreamer

class Classifier(object):
    def __init__(self, trainFeatures, trainLabels, numSamples, labels):
        #Read in labels index mapping
        with open(labels, 'rb') as f:
            labelsDict = f.readline()
            self.labels = ast.literal_eval(labelsDict)
        
        #Store mapping from indices to labels
        self.reverseLabels = {v:k for k,v in self.labels.items()}

        matX = common.load_sparse_csr("../features/" + trainFeatures)
        matY = common.load_sparse_csr("../features/" + trainLabels)

        self.trainFeatures = matX[range(numSamples),:] #Get numSamples entries
        print 'Shape: ', matY.shape
        print 'Shape: ', matX.shape
        self.trainLabels = matY[range(numSamples),:].todense()

    def train(self):
        pass

    def predict(self, testFeatures, testLabels, numSamples):
        matX = common.load_sparse_csr("../features/" + testFeatures)
        matY = common.load_sparse_csr("../features/" + testLabels)

        self.testFeatures = matX[range(numSamples),:] #Get numSamples entries
        self.testLabels = matY[range(numSamples),:].todense()
