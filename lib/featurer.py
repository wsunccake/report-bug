import glob
import json
import re

import nltk
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer


def get_sentence_token(text):
    clean_tokens = []
    tokens = text.split('\n')

    for t in tokens:
        if t is '':
            continue

        tmp_token = t.lower().strip()
        tmp_tokens = (nltk.tokenize.sent_tokenize(tmp_token))
        clean_tokens.extend(tmp_tokens)

    return clean_tokens


def get_word_token(text):
    clean_tokens = []
    tokens = text.split()
    stop_words = nltk.corpus.stopwords.words('english')

    for t in tokens:
        if t[-1] in [',', ':', '.']:
            t = t[:-1]

        # remove session id
        matcher = re.search(r'jsessionid=\w+', t)
        if matcher:
            continue

        # remove time
        matcher = re.search(r'\d+:\d+:\d+', t)
        if matcher:
            continue

        if t in stop_words:
            continue

        tmp_token = t.lower()
        clean_tokens.append(tmp_token)

    return clean_tokens


def get_token(text):
    clean_tokens = []

    for sentence in get_sentence_token(text):
        tokens = get_word_token(sentence)
        clean_tokens.extend(tokens)

    return clean_tokens


def rocchio(train, target):
    from sklearn.neighbors import NearestCentroid
    classifier = NearestCentroid().fit(train, target)
    return classifier


def naive_bayes(train, target):
    from sklearn.naive_bayes import MultinomialNB
    classifier = MultinomialNB().fit(train, target)
    return classifier


def k_mean(train, target):
    from sklearn.neighbors import KNeighborsClassifier
    classifier = KNeighborsClassifier(10).fit(train, target)
    return classifier


def svm(train, target):
    from sklearn import svm
    classifier = svm.SVC(kernel='linear').fit(train, target)
    return classifier


if __name__ == '__main__':
    messages = []
    categories = []

    # train_files = ['train/data.json']
    train_files = glob.glob('train/*.json')
    for input_json in train_files:
        with open(input_json, 'r') as f:
            lines = json.loads(f.read())

        for line in lines:
            messages.append(line['test_message'])
            categories.append(line['reason_id'])

    # vectorize
    count_vector = CountVectorizer(tokenizer=get_token)
    X_train_counts = count_vector.fit_transform(messages)
    # print(count_vector.vocabulary_)

    # tf-idf
    tfidf_transformer = TfidfTransformer()
    X_train_tfidf = tfidf_transformer.fit_transform(X_train_counts)

    classifier = naive_bayes(X_train_tfidf, categories)

    test_json = 't.json'
    fail_messages = []
    with open(test_json, 'r') as f:
        lines = json.loads(f.read())

    for line in lines:
        fail_messages.append(line['test_message'])

    X_test_counts = count_vector.transform(fail_messages)
    X_test_tfidf = tfidf_transformer.transform(X_test_counts)
    predicted = classifier.predict(X_test_tfidf)
    print(predicted)
