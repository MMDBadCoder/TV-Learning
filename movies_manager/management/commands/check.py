import json
import sys
from concurrent.futures import ThreadPoolExecutor

import requests
import tqdm
from django.core.management import BaseCommand

from common_utils.elasticsearch import ElasticConnectionFactory, validate_existence_of_elasticsearch_index
from common_utils.logging_utils import LoggerFactory
from movies_manager.models import Movie

# Create a logger instance
logger = LoggerFactory.get_instance()


class Command(BaseCommand):
    help = 'Check all models are consistent'

    def handle(self, *args, **options):
        if not validate_existence_of_elasticsearch_index():
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
    quotes = None

    if movie.subtitle_file:
        if not movie.visible:
            logger.info(f'"{movie_name}" is not visible but has subtitle file!')
        try:
            quotes = movie.get_quotes()
        except Exception as e:
            logger.error(f'Some problems were detected in subtitle of "{movie_name}"')
            logger.error(e)
            sys.exit(1)

    if not movie.visible:
        return

    if not movie.subtitle_file:
        logger.error(f'"{movie_name}" has no subtitle file.')
        sys.exit(2)

    if quotes is None:
        quotes = movie.get_quotes()

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
        try:
            query = {"query": {"match": {"movie_id": movie.id}}}
            if es.count(index='quotes', body=query)['count'] != len(quotes):
                logger.error(f'Quotes of "{movie_name}" are not synced by elasticsearch.')
                sys.exit(6)
        except Exception as es_error:
            logger.error(f'Unable to get count of quotes of "{movie_name}"')
            logger.error(es_error)
            sys.exit(5)


