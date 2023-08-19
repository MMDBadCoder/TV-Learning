from webvtt import WebVTT

def extract_quotes(vtt_file_path):
    vtt = WebVTT().read(vtt_file_path)
    quotes = []

    for caption in vtt:
        quote = {
            'start': caption.start_in_seconds,
            'end': caption.end_in_seconds,
            'text': caption.text.strip()
        }
        quotes.append(quote)

    return quotes

vtt_file_path = 'path/to/your/subtitle.vtt'
quotes = extract_quotes(vtt_file_path)

for quote in quotes:
    print(f"Start: {quote['start']} - End: {quote['end']}")
    print(f"Text: {quote['text']}")
    print()