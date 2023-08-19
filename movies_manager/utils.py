import os
import string

# Determines subtitle path to be uploaded there
from webvtt import WebVTT


def get_subtitle_path(instance, filename):
    return os.path.join('subtitle_files', f'{instance.id}.vtt')


# This method does thw things:
# 1. Some files have unprintable chars, this method remove them
# 2. .vtt files should begin with 'WEBVTT\n\n', this method will add it if not exist
def prepare_subtitle_file(subtitle_file_path):
    temp_file_path = subtitle_file_path + ".temp"
    printable_chars = bytes(string.printable, 'ascii')
    with open(subtitle_file_path, "rb") as in_file, open(temp_file_path, "wb") as out_file:
        read_chars = []

        # Read
        for b in in_file.read():
            if b in printable_chars:
                read_chars.append(b)

        # Concatenate WEBVTT
        printable_bytes = bytes(read_chars)
        if chr(read_chars[0]).lower() != 'w':
            printable_bytes = bytes('WEBVTT\n\n', 'utf-8') + printable_bytes

        # Write
        out_file.write(printable_bytes)

    os.remove(subtitle_file_path)
    os.rename(temp_file_path, subtitle_file_path)


# Extract all quotes in a .vtt file
def extract_quotes_from_subtitle(vtt_file_path):
    vtt = WebVTT().read(vtt_file_path)
    quotes = []
    for caption in vtt:
        index = 0
        if caption.identifier.isnumeric():
            index = int(caption.identifier)
        quote = {
            'index': index,
            'start_time': caption.start_in_seconds,
            'end_time': caption.end_in_seconds,
            'duration': caption.end_in_seconds - caption.start_in_seconds,
            'text': caption.text.strip()
        }
        quotes.append(quote)
    return quotes
