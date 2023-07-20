import re

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from tqdm import tqdm

# ------------- call for first time -------------
nltk.download('stopwords')
nltk.download('punkt')

simple_word_pattern = re.compile('^[a-z]+$')

english_stops = set(stopwords.words('english'))

frequency_of_word = {}


def extract_words_of_file(file_path):
    with open(file_path, 'r') as reading_file:
        for line in tqdm(reading_file.readlines()):
            words = word_tokenize(line)
            for word in words:
                word = word.lower()
                if word in english_stops:
                    continue
                if not simple_word_pattern.match(word):
                    continue
                if not frequency_of_word.__contains__(word):
                    frequency_of_word[word] = 0
                frequency_of_word[word] += 1


if __name__ == '__main__':

    with open('./stop_words.csv', 'w') as stop_words_file:
        for word in english_stops:
            stop_words_file.write(word + '\n')

    extract_words_of_file('./plain_english_text.txt')
    print('Reading samples finished')

    # writing result
    sorted_words = sorted(frequency_of_word.items(), key=lambda x: x[1], reverse=True)
    with open('frequency.csv', 'w') as output_file:
        for word, frequency in sorted_words:
            output_file.write(word + ', ' + str(frequency) + '\n')

    print('Result is written')
