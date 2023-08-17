import sys

from django.core.management import BaseCommand
from tqdm import tqdm
import codecs

from movies_manager.models import Movie
from quote_searcher.connection import ConnectionFactory


class Command(BaseCommand):
    help = 'Check all models are consistent'

    def handle(self, *args, **options):

        # Checking health of subtitle files
        for movie in tqdm(Movie.objects.all()):
            if not movie.has_subtitle_file():
                continue

            try:
                movie.get_quotes()
            except Exception:
                remove_bom(movie.get_subtitle_file_path(), movie.get_subtitle_file_path())
                try:
                    movie.get_quotes()
                except Exception as e:
                    print('Problem at reading subtitle of {} by id of {}'.format(movie.title1, movie.id))
                    print(e)
                    sys.exit(1)

            # Check if vtt file has been generated
            try:
                movie.check_to_generate_vtt_file()
            except Exception as e:
                print('Can not generate vtt file')
                print(e)
                sys.exit(1)

        print("✅ All subtitle files are ok")

        # Check if all visible movies are ready to searching on their quotes
        with ConnectionFactory.create_new_connection() as es:
            for movie in tqdm(Movie.objects.filter(hidden_to_users=False)):

                # Check if it has subtitle file
                if not movie.has_subtitle_file():
                    print('{} with id of {} does not have subtitle file'.format(movie.title1, movie.id))
                    sys.exit(2)

                # Check if it hae stream url
                if not movie.video_stream_url:
                    print('{} with id of {} does not have video stream url'.format(movie.title1, movie.id))
                    sys.exit(3)

                movie_quotes = movie.get_quotes()

                def get_quotes_count_in_elasticsearch():
                    query = {"query": {"match": {"movie_id": movie.id}}}
                    return es.count(index='quotes', body=query)['count']

                # Check if its quotes are inserted elasticsearch
                if (not movie.is_inserted_in_elasticsearch) or \
                        (len(movie_quotes) != get_quotes_count_in_elasticsearch()):
                    try:
                        movie.insert_quotes_to_elasticsearch()

                        # Check if count of inserted quotes are correct
                        if len(movie_quotes) != get_quotes_count_in_elasticsearch():
                            print(
                                "Quotes counts of subtitle file and elasticsearch are not same for {} by id of {}"
                                .format(movie.title1, movie.id))
                            sys.exit(4)

                    except Exception as e:
                        print('Can not insert quotes of {} by id of {} to elasticsearch', movie.title1, movie.id)
                        print(e)
                        sys.exit(5)

        print("✅ All not hidden movies are ready to search")


# Bom is a bad char that will be appeared at starting of srt files
def remove_bom(input_file, output_file):
    with codecs.open(input_file, 'r', encoding='utf-8-sig') as file:
        content = file.read()

    # Remove BOM if present
    content = content.lstrip('\ufeff')
    content = content.replace('\ufeff', '')

    with codecs.open(output_file, 'w', encoding='utf-8') as file:
        file.write(content)
