import json
import os
import string
import sys
from concurrent.futures import ThreadPoolExecutor

import requests
import tqdm
from django.core.management import BaseCommand

from common_utils.elasticsearch import ElasticConnectionFactory
from common_utils.logging_utils import LoggerFactory
from movies_manager.models import Movie

# Create a logger instance
logger = LoggerFactory.get_instance()


class Command(BaseCommand):
    help = 'Check all models are consistent'

    def handle(self, *args, **options):
        logger.info('Check healthy of elasticsearch')
        if not check_exists_of_elasticsearch_index():
            sys.exit(99)

        # Create a ThreadPoolExecutor to check healthy of each movie
        futures = []
        with ThreadPoolExecutor(5) as executor:
            for movie in Movie.objects.all():
                futures.append(executor.submit(check_healthy_of_movie, movie))

            # Retrieve the results of tasks
            for future in tqdm.tqdm(futures):
                try:
                    future.result()
                except Exception as e:
                    logger.error('An error occurred when checking healthy of movies')
                    logger.error(e)

        logger.info("✅ All visible movies are ready for search")


def check_healthy_of_movie(movie: Movie):
    movie_name = f'{movie.title1[:10]}...(id={movie.id})'

    if movie.has_subtitle_file():
        if not movie.visible:
            logger.info(f'"{movie_name}" is not visible but has subtitle file!')
        try:
            movie.get_quotes()
        except Exception as e:
            logger.warning(f'Some problems were detected in subtitle of "{movie_name}".\n{e}')
            remove_unprintable_chars(movie.get_subtitle_file_path())
            try:
                movie.get_quotes()
            except Exception as e:
                logger.error(f'Problem at reading subtitle of "{movie_name}".')
                logger.error(e)
                sys.exit(1)

    if not movie.visible:
        return

    if not movie.has_subtitle_file():
        logger.error(f'"{movie_name}" has no subtitle file.')
        sys.exit(2)

    # Check if vtt file has been generated
    try:
        movie.try_to_generate_vtt_file()
    except Exception as e:
        logger.error(f'Can not generate vtt file of "{movie_name}".')
        logger.error(e)
        sys.exit(3)

    # Check if streaming url is healthy
    successful = True
    try:
        response = requests.head(movie.video_stream_url())
        if response.status_code != requests.codes.ok:
            successful = False
            logger.error(f'Streaming URL of "{movie_name}" is not available.')
    except requests.RequestException as e:
        successful = False
        logger.error(f'An error occurred while checking the streaming url of "{movie_name}".')
        logger.error(e)
    if not successful:
        sys.exit(4)

    # Check if all visible movies are ready to searching on their quotes
    with ElasticConnectionFactory.create_new_connection() as es:

        expected_quotes = movie.get_quotes()

        def get_quotes_count_from_elasticsearch():
            try:
                query = {"query": {"match": {"movie_id": movie.id}}}
                return es.count(index='quotes', body=query)['count']
            except Exception as es_error:
                logger.error(f'Unable to get count of quotes of "{movie_name}"')
                logger.error(es_error)
                sys.exit(5)

        # Check if its quotes are inserted elasticsearch
        if (not movie.is_inserted_in_elasticsearch) or (len(expected_quotes) != get_quotes_count_from_elasticsearch()):
            try:
                logger.info(f'Try to insert "{movie_name}" quotes to elasticsearch.')
                movie.insert_quotes_to_elasticsearch()
            except Exception as e:
                logger.error(f'Can not put quotes of "{movie_name}" to elasticsearch.')
                logger.error(e)
                sys.exit(6)


# Some .srt files have unprintable chars, this method remove them
def remove_unprintable_chars(subtitle_file_path):
    temp_file_path = subtitle_file_path + ".temp"
    printable_chars = bytes(string.printable, 'ascii')
    with open(subtitle_file_path, "rb") as in_file, open(temp_file_path, "wb") as out_file:
        printable_bytes = []
        for b in in_file.read():
            if b in printable_chars:
                printable_bytes.append(b)
        out_file.write(bytes(printable_bytes))
    os.remove(subtitle_file_path)
    os.rename(temp_file_path, subtitle_file_path)


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
