#!/usr/bin/env python3
import glob
import json
import os

import joblib
from fire import Fire
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer

from featurer import Token, Classifier

CLASSIFIER_MODEL = {'svm': Classifier.svm, 'nb': Classifier.naive_bayes, 'knn': Classifier.k_mean}


class TrainingModel:
    def __init__(self, train_folder, model):
        self.train_folder = train_folder
        self.model = model

        self._count_vector_joblib = f'{train_folder}/count_vector.joblib'
        self._tfidf_transformer_joblib = f'{train_folder}/tfidf_transformer.joblib'
        self._model_joblib = f'{train_folder}/{model}.joblib'

        self.count_vector = CountVectorizer(tokenizer=Token.token)
        self.tfidf_transformer = TfidfTransformer()
        self.classifier = None

    def load_data(self):
        self.count_vector = joblib.load(self._count_vector_joblib)
        self.tfidf_transformer = joblib.load(self._tfidf_transformer_joblib)
        self.classifier = joblib.load(self._model_joblib)

    def save_data(self):
        joblib.dump(self.count_vector, self._count_vector_joblib)
        joblib.dump(self.tfidf_transformer, self._tfidf_transformer_joblib)
        joblib.dump(self.classifier, self._model_joblib)

    def train_data(self):
        messages = []
        categories = []
        train_files = glob.glob(f'{self.train_folder}/*.json')

        for input_json in train_files:
            with open(input_json, 'r') as f:
                lines = json.loads(f.read())

            for line in lines:
                messages.append(line['test_message'])
                categories.append(line['reason_id'])

        x_train_counts = self.count_vector.fit_transform(messages)
        x_train_tfidf = self.tfidf_transformer.fit_transform(x_train_counts)
        self.classifier = CLASSIFIER_MODEL[self.model](x_train_tfidf, categories)

        return self.classifier, self.count_vector, self.tfidf_transformer

    def train(self):
        train_files_time = -float('inf')
        train_files = glob.glob(f'{self.train_folder}/*.json')
        for f in train_files:
            t = os.path.getmtime(f)
            train_files_time = t if t > train_files_time else train_files_time

        joblib_time = float('inf')
        joblib_files = [self._count_vector_joblib, self._tfidf_transformer_joblib, self._model_joblib]
        for f in joblib_files:
            if os.path.exists(f):
                t = os.path.getmtime(f)
                joblib_time = t if t < joblib_time else joblib_time
            else:
                joblib_time = 0.0

        if train_files_time > joblib_time:
            self.train_data()
            self.save_data()
        else:
            self.load_data()

        return self.classifier, self.count_vector, self.tfidf_transformer

    def predict(self, test_file):
        fail_messages = []
        with open(test_file, 'r') as f:
            lines = json.loads(f.read())

        for line in lines:
            fail_messages.append(line['test_message'])

        x_test_counts = self.count_vector.transform(fail_messages)
        x_test_tfidf = self.tfidf_transformer.transform(x_test_counts)
        predicted = self.classifier.predict(x_test_tfidf)

        return predicted


def predict_bug(test_file, train_folder, model):
    training_model = TrainingModel(train_folder, model)
    training_model.train()
    predicted = training_model.predict(test_file)
    print(predicted)


if __name__ == '__main__':
    Fire(predict_bug)
