from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.decomposition import PCA
from sklearn.feature_selection import SelectKBest, chi2
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
import argparse, os, sys
from time import time
from pprint import pprint
import numpy as np

root_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(root_dir)
from util.common import load_sparse_csr, get_dataset_for_class
from util.DataStreamer import DataStreamer
from features.extractors import *

parser = argparse.ArgumentParser(description = 'does hyperparameter tuning')
parser.add_argument('trainExamplesZip', type = str, help = 'bz2 file for training examples')
parser.add_argument('trainLabels', type = str, help = 'labels file for training pipeline')
parser.add_argument('testExamplesZip', type = str, help = 'bz2 file for test examples')
parser.add_argument('testLabels', type = str, help = 'labels file for training pipeline')
args = parser.parse_args()

print 'loading datasets'
Ytrain = load_sparse_csr(args.trainLabels).todense()
Ytest = load_sparse_csr(args.testLabels).todense()

train_scores = []
test_scores = []

for k in range(Ytrain.shape[1]):
    train_examples_generator = DataStreamer.load_from_bz2(args.trainExamplesZip)
    test_examples_generator = DataStreamer.load_from_bz2(args.testExamplesZip)

    print("Training class %s ..." % k)

    # get training examples
    examples, Y = get_dataset_for_class(k, train_examples_generator, Ytrain, fair_sampling=False, restrict_sample_size=1000)

    pipeline = Pipeline([
        ('ngrams', FeatureUnion([
            ('title', TitleNgramsExtractor()),
            ('body', BodyNgramsExtractor()),
            ('code', CodeNgramsExtractor()),
            ('label', LabelCountsExtractor()),
            ('pygment', PygmentExtractor()),
        ])),
        ('clf', LogisticRegression()),
    ])

    print("pipeline:", [name for name, _ in pipeline.steps])
    pipeline.fit(examples, Y)
    Ypred = pipeline.predict(examples)
    scores = {
        'precision': precision_score(Y, Ypred),
        'recall': recall_score(Y, Ypred),
        'f1': f1_score(Y, Ypred)
    }

    t0 = time()
    print("done in %0.3fs" % (time() - t0))
    print("Train score")
    pprint(scores)

    train_scores += [scores]

    examples, Y = get_dataset_for_class(k, test_examples_generator, Ytest, fair_sampling=False)
    Ypred = pipeline.predict(examples)
    scores = {
        'precision': precision_score(Y, Ypred),
        'recall': recall_score(Y, Ypred),
        'f1': f1_score(Y, Ypred)
    }
    print("Test score:")
    pprint(scores)

    test_scores += [scores]

train_ave = {
    'accuracy': np.mean([d['accuracy'] for d in train_scores]),
    'precision': np.mean([d['precision'] for d in train_scores]),
    'recall': np.mean([d['precision'] for d in train_scores]),
    'f1': np.mean([d['precision'] for d in train_scores]),
}

test_ave = {
    'accuracy': np.mean([d['accuracy'] for d in test_scores]),
    'precision': np.mean([d['precision'] for d in test_scores]),
    'recall': np.mean([d['precision'] for d in test_scores]),
    'f1': np.mean([d['precision'] for d in test_scores]),
}

print 'Train average:'
pprint(train_ave)

print 'Test average'
pprint(test_ave)