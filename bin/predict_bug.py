#!/usr/bin/env python3
import glob
import json

from fire import Fire
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer

from featurer import Token, Classifier

Classifier_Model = {'svm': Classifier.svm, 'nb': Classifier.naive_bayes, 'knn': Classifier.k_mean}


def train_data(train_folder, model):
    messages = []
    categories = []

    train_files = glob.glob(f'{train_folder}/*.json')
    for input_json in train_files:
        with open(input_json, 'r') as f:
            lines = json.loads(f.read())

        for line in lines:
            messages.append(line['test_message'])
            categories.append(line['reason_id'])

    count_vector = CountVectorizer(tokenizer=Token.token)
    x_train_counts = count_vector.fit_transform(messages)

    tfidf_transformer = TfidfTransformer()
    x_train_tfidf = tfidf_transformer.fit_transform(x_train_counts)

    classifier = Classifier_Model[model](x_train_tfidf, categories)
    return classifier, count_vector, tfidf_transformer


def predict(test_file, train_folder, model):
    classifier, count_vector, tfidf_transformer = train_data(train_folder, model)

    fail_messages = []
    with open(test_file, 'r') as f:
        lines = json.loads(f.read())

    for line in lines:
        fail_messages.append(line['test_message'])

    x_test_counts = count_vector.transform(fail_messages)
    x_test_tfidf = tfidf_transformer.transform(x_test_counts)
    predicted = classifier.predict(x_test_tfidf)
    print(predicted)


if __name__ == '__main__':
    Fire(predict)
