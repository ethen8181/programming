import os
import re
import csv
import sys
import glob
from tqdm import tqdm
from nltk.corpus import stopwords


STOPWORDS = set(stopwords.words('english'))


class CsvTextPreprocessor:

    def __init__(self, original_text_dir, normalized_text_dir, stopwords=None):
        self.stopwords = stopwords
        self.original_text_dir = original_text_dir
        self.normalized_text_dir = normalized_text_dir

    def preprocess(self, input_dir, content_index):
        for directory in (self.original_text_dir, self.normalized_text_dir):
            if not os.path.isdir(directory):
                os.makedirs(directory, exist_ok=True)

        if self.stopwords is None:
            self.stopwords_ = STOPWORDS
        else:
            self.stopwords_ = self.stopwords

        csv.field_size_limit(sys.maxsize)

        doc_id = 0
        text_files = os.path.join(input_dir, '*.csv')
        for file_path in glob.iglob(text_files):
            with open(file_path, 'r') as fin:
                reader = csv.reader(fin)

                # skip the header
                next(reader)
                for line in tqdm(reader):
                    try:
                        content = line[content_index]
                        normalized_content = normalize_text(content, self.stopwords_)
                        self.write_to_file(doc_id, content, normalized_content)
                        doc_id += 1
                    except IndexError:
                        print('erroring parsing: ', line)

    def write_to_file(self, doc_id, content, normalized_content):
        file_name = 'doc' + str(doc_id) + '.txt'
        original_text_path = os.path.join(self.original_text_dir, file_name)
        normalized_text_path = os.path.join(self.normalized_text_dir, file_name)
        with open(original_text_path, 'w') as fout1, open(normalized_text_path, 'w') as fout2:
            fout1.write(content)
            fout2.write(normalized_content)


def normalize_text(text, stopwords=STOPWORDS):

    # remove special characters\whitespaces
    text = re.sub(r'[^a-zA-Z\s]', '', text, re.I | re.A)

    # lower case & tokenize text
    tokens = re.split(r'\s+', text.lower().strip())

    # filter stopwords out of text &
    # re-create text from filtered tokens
    text = ' '.join(token for token in tokens if token not in stopwords)
    return text
