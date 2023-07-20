from english_words_difficulty.difficulty_service import Difficulty
from subtitle_utils.utils import get_quotes_of_subtitle

difficulty_instance = Difficulty.get_instance()

subtitle_path = '/home/mohammad/Desktop/Cast.Away.2000.1080p.BluRay.H264.AAC-RARBG.srt'
quotes = get_quotes_of_subtitle(subtitle_path)
full_text = '\n'.join([quote['text'] for quote in quotes])
print(difficulty_instance.get_difficulty_of_text(full_text))
