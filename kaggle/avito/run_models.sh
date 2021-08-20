#!/usr/bin/env bash

set -e

BASE_DIR=`cd $(dirname $0) && pwd`
SOURCE_DIR=${BASE_DIR}/src

python ${SOURCE_DIR}/modeling_pipeline_kernel.py --text_feature_method tfidf --model_method lightgbm
#python ${SOURCE_DIR}/modeling_pipeline_train_test.py --text_feature_method tfidf --model_method fm
#python ${SOURCE_DIR}/modeling_pipeline_train_test.py --text_feature_method tfidf --model_method lightgbm
#python ${SOURCE_DIR}/modeling_pipeline_train_test.py --text_feature_method fasttext --model_method fm
#python ${SOURCE_DIR}/modeling_pipeline_train_test.py --text_feature_method fasttext --model_method lightgbm