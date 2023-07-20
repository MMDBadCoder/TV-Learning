import math

import nltk as nltk
from nltk.tokenize import word_tokenize

# ------------- call for first time -------------
nltk.download('stopwords')
nltk.download('punkt')


class Difficulty:
    __instance = None

    @staticmethod
    def get_instance():
        if Difficulty.__instance is None:
            Difficulty.__instance = Difficulty()
        return Difficulty.__instance

    def __init__(self):
        self.__frequency_by_word = {}
        self.total_words_count = 0

        with open('./english_words_difficulty/frequency.csv', 'r') as frequency_file:
            for line in frequency_file.readlines():
                parts = line.split(',')
                word = parts[0].strip()
                frequency = int(parts[1].strip())
                self.__frequency_by_word[word] = frequency
                self.total_words_count += frequency

        stop_words = []
        with open('./english_words_difficulty/stop_words.csv', 'r') as stop_words_file:
            for word in stop_words_file.readlines():
                word = word.strip()
                stop_words.append(word)

        self.stop_words = set(stop_words)

    def get_difficulty_of_word(self, word):
        word = word.lower()

        if self.stop_words.__contains__(word):
            return 0

        frequency = 1
        if self.__frequency_by_word.__contains__(word):
            frequency = self.__frequency_by_word[word]

        return math.log2(self.total_words_count / frequency)

    def get_difficulty_of_text(self, text):
        words = word_tokenize(text)
        difficulties = [self.get_difficulty_of_word(word) for word in words]
        return sum(difficulties) / len(difficulties)
