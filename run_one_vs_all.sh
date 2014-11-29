#!/usr/bin/env bash

split_data=1
extract_features=1
tune_hyper=0

features='ngrams' # choose between ngrams, ngramsTitle, ngramsCode, topLabels, NER
unigramfeatures='ngrams'

# Data collection
top_labels=20 #how many labels to predict?
min_count=100 #how many examples per label at least?

test_fraction=0.15 #how much to use for test
val_fraction=0.15 #how much to use for tuning

# Feature extraction
cutoff=10 #frequency cutoff for rare ngrams
vectorizer_type=count

prefix=top${top_labels}min${min_count}

mkdir experiments

if [ $split_data -eq 1 ]
then
  echo "splitting data for top ${top_labels} labels and minimum ${min_count} train examples per label"
  python util/split_data.py full_data/Train.csv.bz2 full_data/tags.count.pkl experiments/${prefix} --top_n_labels $top_labels --min_count $min_count --test_fraction $test_fraction --val_fraction $val_fraction
  # now extract labels
  python util/extract_labels.py experiments/${prefix}.train.bz2 experiments/${prefix}.labels.counts.json experiments/${prefix}.train.Y
  python util/extract_labels.py experiments/${prefix}.val.bz2 experiments/${prefix}.labels.counts.json experiments/${prefix}.val.Y
  python util/extract_labels.py experiments/${prefix}.test.bz2 experiments/${prefix}.labels.counts.json experiments/${prefix}.test.Y
fi

if [ $extract_features -eq 1 ]
then
  echo "extracting features"
  # the first time will produce a vocab file
  python util/extract_features.py \
  --top_labels_labels experiments/${prefix}.labels.counts.json \
  --ngrams_unigrams \
  --ngrams_cutoff $cutoff \
  --ngrams_title_unigrams \
  --ngrams_title_binarize \
  --ngrams_title_cutoff 1 \
  --ngrams_code_binarize \
  --ngrams_code_cutoff $cutoff \
  --vectorizer_type $vectorizer_type \
  --NER_code_unigrams \
  --NER_code_binarize \
  --NER_code_cutoff 1\
  experiments/${prefix}.train.bz2 \
  experiments/${prefix}.train \
  $features

  # the other times we use the produced vocab file
  python util/extract_features.py \
  --top_labels_labels experiments/${prefix}.labels.counts.json \
  --ngrams_unigrams \
  --ngrams_cutoff $cutoff \
  --ngrams_vocab experiments/${prefix}.train.vocab.json \
  --ngrams_title_unigrams \
  --ngrams_title_binarize \
  --ngrams_title_cutoff 1 \
  --ngrams_title_vocab experiments/${prefix}.train.title.vocab.json \
  --ngrams_code_binarize \
  --ngrams_code_cutoff $cutoff \
  --ngrams_code_vocab experiments/${prefix}.train.code.vocab.json \
  --vectorizer_type $vectorizer_type \
  --NER_code_unigrams \
  --NER_code_binarize \
  --NER_code_cutoff 1\
  --NER_code_vocab experiments/${prefix}.train.NER.code.vocab.json \
    experiments/${prefix}.val.bz2 \
  experiments/${prefix}.val \
  $features

  python util/extract_features.py \--top_labels_labels experiments/${prefix}.labels.counts.json \
  --ngrams_unigrams \
  --ngrams_cutoff $cutoff \
  --ngrams_vocab experiments/${prefix}.train.vocab.json \
  --ngrams_title_unigrams \
  --ngrams_title_binarize \
  --ngrams_title_cutoff 1 \
  --ngrams_title_vocab experiments/${prefix}.train.title.vocab.json \
  --ngrams_code_binarize \
  --ngrams_code_cutoff $cutoff \
  --ngrams_code_vocab experiments/${prefix}.train.code.vocab.json \
  --vectorizer_type $vectorizer_type \
  --NER_code_unigrams \
  --NER_code_binarize \
  --NER_code_cutoff 1 \
  --NER_code_vocab experiments/${prefix}.train.NER.code.vocab.json \
  experiments/${prefix}.test.bz2 \
  experiments/${prefix}.test \
  $features
fi

if [ $tune_hyper -eq 1 ]
then
    echo "doing hyperparameter tuning for each class"
    python util/tune_hyper.py \
	experiments/${prefix}.train.X \
	experiments/${prefix}.train.Y \
	experiments/tuning/${prefix}.tuned \
	--parallel 10
fi
#else
    #echo "training/testing for each class"
    #python util/train_test.py \
	#experiments/${prefix}.train.X \
	#experiments/${prefix}.train.Y \
	#experiments/${prefix}.val.X \
	#experiments/${prefix}.val.Y
#fi
