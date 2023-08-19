import re

import html2text

from english_words_difficulty.difficulty_service import Difficulty

WORDS_DIFFICULTY = 'words_difficulty'
SPEED_OF_SPEACH = 'speed_of_speech'


def get_milly_second_of_quote_by_subtitle_format(time: str):
    parts = time.split(':')
    hour = int(parts[0])
    minutes = int(parts[1])
    seconds = parts[2]
    seconds = float(seconds)
    return (hour * 60 * 60) + (minutes * 60) + seconds


# We pass a vtt_file_path to write clean format of subtitle at it
def get_quotes_of_subtitle(subtitle_path):
    quotes = []

    def create_quote(quote, quote_lines):
        quote['text'] = '\n'.join(quote_lines)
        quotes.append(quote)

    with open(subtitle_path, 'r') as subtitle_file:
        state = 0

        # state 0: except to reading an int (index of subtitle part)
        # state 1: except to reading time
        # state 2: reading subtitle text

        line_number = 0
        try:
            current_quote = {}
            for line in subtitle_file.readlines():
                line_number += 1
                line = line.strip()
                if state == 0:
                    if not line:
                        continue
                    current_quote = {
                        'index': int(line)
                    }
                    state = 1
                elif state == 1:
                    line = line.replace(',', '.')
                    parts = line.split(' --> ')
                    current_quote['start_time'] = get_milly_second_of_quote_by_subtitle_format(parts[0])
                    current_quote['end_time'] = get_milly_second_of_quote_by_subtitle_format(parts[1])
                    current_quote['duration'] = current_quote['end_time'] - current_quote['start_time']
                    current_quote_lines = []
                    state = 2
                elif state == 2:
                    if line == '':
                        create_quote(current_quote, current_quote_lines)
                        state = 0
                    else:
                        current_quote_lines.append(line)

            if state == 2:
                create_quote(current_quote, current_quote_lines)

        except Exception as e:
            raise Exception('Error at line {}'.format(line_number), e)

    return quotes


def get_difficulty_of_subtitle(subtitle_path):
    difficulty_instance = Difficulty.get_instance()
    quotes = get_quotes_of_subtitle(subtitle_path)
    sum_of_duration = sum([quote['duration'] for quote in quotes])
    sum_of_quote_length = sum([len(quote['text']) for quote in quotes])
    full_text = '\n'.join([quote['text'] for quote in quotes])

    return {
        WORDS_DIFFICULTY: difficulty_instance.get_difficulty_of_text(full_text),
        SPEED_OF_SPEACH: sum_of_quote_length / sum_of_duration
    }


def generate_vtt_file(subtitle_path, vtt_file_path):
    time_range_line_format = re.compile('\d{2}:\d{2}:\d{2}(,\d+)? --> \d{2}:\d{2}:\d{2}(,\d+)?')
    with open(subtitle_path, 'r') as subtitle_file:
        with open(vtt_file_path, 'w') as vtt_output_file:
            vtt_output_file.write('WEBVTT\n\n')
            for line in subtitle_file.readlines():
                if time_range_line_format.match(line):
                    line = line.replace(',', '.')
                else:
                    line = html2text.html2text(line)
                line = line.replace('\n', '').replace("_", "").replace("\\", '')
                vtt_output_file.write(line + '\n')
