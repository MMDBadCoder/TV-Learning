from subtitle_utils.utils import get_difficulty_of_subtitle, WORDS_DIFFICULTY, SPEED_OF_SPEACH

for i in [1, 2, 3, 4, 6, 7, 10]:
    subtitle_path = 'subtitle_files/{}.srt'.format(i)
    difficulty = get_difficulty_of_subtitle(subtitle_path)
    print("{}: {}".format(i, difficulty[WORDS_DIFFICULTY] + difficulty[SPEED_OF_SPEACH]))
