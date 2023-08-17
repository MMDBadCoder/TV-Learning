import codecs
import json
import sys

import requests
from django.core.management import BaseCommand

from common_utils.elasticsearch import ElasticConnectionFactory
from common_utils.logging_utils import LoggerFactory
from movies_manager.models import Movie

# Create a logger instance
logger = LoggerFactory.get_instance()


class Command(BaseCommand):
    help = 'Check all models are consistent'

    def handle(self, *args, **options):
        if not check_exists_of_elasticsearch_index():
            sys.exit(99)

        for movie in Movie.objects.all():
            check_healthy_of_movie(movie)

        logger.info("✅ All visible movies are ready to search")


def check_healthy_of_movie(movie: Movie):
    if movie.has_subtitle_file():
        if not movie.visible:
            logger.info(f'"{movie}" is not visible but has subtitle file!')
        try:
            movie.get_quotes()
        except Exception as e:
            logger.warning(f'Some problems were detected in subtitle of "{movie.title1}".\n{e}')
            remove_bom(movie.get_subtitle_file_path(), movie.get_subtitle_file_path())
            try:
                movie.get_quotes()
            except Exception as e:
                logger.error(f'Problem at reading subtitle of "{movie.title1}".')
                logger.error(e)
                sys.exit(1)

    if not movie.visible:
        return

    if not movie.has_subtitle_file():
        logger.error(f'"{movie.title1}" has no subtitle file.')
        sys.exit(2)

    # Check if vtt file has been generated
    try:
        movie.try_to_generate_vtt_file()
    except Exception as e:
        logger.error(f'Can not generate vtt file of "{movie.title1}".')
        logger.error(e)
        sys.exit(3)

    # Check if streaming url is healthy
    successful = True
    try:
        response = requests.head(movie.video_stream_url())
        if response.status_code == requests.codes.ok:
            successful = False
            logger.error(f'Streaming URL of "{movie.title1}" is not available.')
    except requests.RequestException:
        successful = False
        logger.error(f'An error occurred while checking the streaming url of "{movie.title1}".')
    if not successful:
        sys.exit(4)

    # Check if all visible movies are ready to searching on their quotes
    with ElasticConnectionFactory.create_new_connection() as es:

        expected_quotes = movie.get_quotes()

        def get_quotes_count_from_elasticsearch():
            query = {"query": {"match": {"movie_id": movie.id}}}
            return es.count(index='quotes', body=query)['count']

        # Check if its quotes are inserted elasticsearch
        if (not movie.is_inserted_in_elasticsearch) or (len(expected_quotes) != get_quotes_count_from_elasticsearch()):
            try:
                movie.insert_quotes_to_elasticsearch()

                # Check if count of inserted quotes are correct
                if len(expected_quotes) != get_quotes_count_from_elasticsearch():
                    logger.error(f'Quotes counts of subtitle file and elasticsearch are not same for "{movie.title1}".')
                    sys.exit(5)

            except Exception as e:
                logger.error(f'Can not put quotes of "{movie.title1}" to elasticsearch.')
                logger.error(e)
                sys.exit(6)


# Bom is a type of bad char that will be appeared at starting of srt files, this method try to remove bom chars
def remove_bom(input_file, output_file):
    with codecs.open(input_file, 'r', encoding='utf-8-sig') as file:
        content = file.read()

    # Remove BOM if present
    content = content.lstrip('\ufeff')
    content = content.replace('\ufeff', '')

    with codecs.open(output_file, 'w', encoding='utf-8') as file:
        file.write(content)


def check_exists_of_elasticsearch_index():
    index_name = 'quotes'
    with ElasticConnectionFactory.create_new_connection() as es:
        if es.indices.exists(index=index_name):
            return True

        with open('quote_searcher/quotes_index_schema.json', 'r') as schema_file:
            schema = json.loads(''.join(schema_file.readlines()))

        # Create the index
        response = es.indices.create(index=index_name, body=schema)
        if response['acknowledged']:
            logger.info(f"Index '{index_name}' created successfully.")
            return True
        else:
            logger.info(f"Failed to create index '{index_name}'.")
            return False
