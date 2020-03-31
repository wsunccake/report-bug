from lib.parser import ReportParser
from lib.parser import ParserTool

import nltk.tokenize
import nltk.corpus
import nltk.stem

from nltk.corpus import wordnet
from nltk import pos_tag
from nltk.tokenize.toktok import ToktokTokenizer

from collections import Counter


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
    # tokens = nltk.tokenize.word_tokenize(text)
    # tokens = nltk.tokenize.wordpunct_tokenize(text)

    stopwords = nltk.corpus.stopwords.words('english')
    stemmer = nltk.stem.PorterStemmer()

    for t in tokens:
        if t in stopwords:
            continue
        tmp_token = stemmer.stem(t)
        clean_tokens.append(tmp_token)

    return clean_tokens


if __name__ == '__main__':

    input_xml = '/tmp/output.xml'
    report_parser = ReportParser(input_xml)
    test_entities = ParserTool.analyze_tests(report_parser.failed_tests)

    lines = ParserTool.extract_test_keyword_message(test_entities)
    for line in lines:
        print('test case: ', line['test'])
        print(line['test_message'])

        # sentence
        # tokens = get_sentence_token(line['test_message'])

        # word
        tokens = get_word_token(line['test_message'])

        # tt = ToktokTokenizer()
        # t4 = tt.tokenize(line['test_message'])

        print('tokens: ', tokens)
        print(Counter(tokens))
