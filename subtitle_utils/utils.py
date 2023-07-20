def get_milly_second_of_movie_by_subtitle_format(time: str):
    parts = time.split(':')
    hour = int(parts[0])
    minutes = int(parts[1])
    seconds = parts[2]
    seconds = seconds.replace(',', '.')
    seconds = float(seconds)
    return (hour * 60 * 60) + (minutes * 60) + seconds


def get_quotes_of_subtitle(subtitle_path):
    quotes = []
    with open(subtitle_path, 'r') as subtitle_file:
        state = 0
        # state 0: except to reading an int (index of subtitle part)
        # state 1: except to reading time
        # state 2: reading subtitle text

        quote = {}
        for line in subtitle_file.readlines():
            line = line.strip()
            if state == 0:
                quote = {
                    'index': int(line)
                }
                state = 1
            elif state == 1:
                parts = line.split(' --> ')
                quote['start_time'] = get_milly_second_of_movie_by_subtitle_format(parts[0])
                quote['end_time'] = get_milly_second_of_movie_by_subtitle_format(parts[1])
                quote['duration'] = quote['end_time'] - quote['start_time']
                quote_lines = []
                state = 2
            elif state == 2:
                if line == '':
                    quote['text'] = '\n'.join(quote_lines)
                    quotes.append(quote)
                    state = 0
                else:
                    quote_lines.append(line)
    return quotes
