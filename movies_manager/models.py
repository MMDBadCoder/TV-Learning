import os

from django.db import models
from elasticsearch import helpers

from TV_LEARNING.settings import BASE_DIR, NGINX_URL
from common_utils.elasticsearch import ElasticConnectionFactory
from common_utils.subtitle_utils import get_quotes_of_subtitle, generate_vtt_file


# Create your models here.

class Movie(models.Model):
    __CASHED_QUOTES = {}

    title1 = models.CharField(max_length=100, blank=False, null=False)
    title2 = models.CharField(max_length=100, blank=False, null=False)
    genre = models.CharField(max_length=100, blank=True, null=False, default='')
    votes_count = models.IntegerField(blank=False, null=False)
    imdb_rating = models.FloatField(blank=False, null=False)
    visible = models.BooleanField(default=False, blank=False, null=False)
    is_inserted_in_elasticsearch = models.BooleanField(default=False, blank=False, null=False)

    def __str__(self):
        return '-'.join([str(self.id), self.title1])

    def video_stream_url(self):
        return f'{NGINX_URL}{self.id}.mp4'

    def get_subtitle_file_path(self):
        return os.path.join(BASE_DIR, 'subtitle_files', str(self.id) + ".srt")

    def has_subtitle_file(self):
        subtitle_file_path = self.get_subtitle_file_path()
        return os.path.isfile(subtitle_file_path)

    def try_to_generate_vtt_file(self):
        subtitle_file_path = self.get_subtitle_file_path()
        vtt_file_path = subtitle_file_path.replace('subtitle_files', 'static/web-subtitles').replace('.srt', '.vtt')
        if not os.path.isfile(vtt_file_path):
            generate_vtt_file(self.get_subtitle_file_path(), vtt_file_path)

    def get_quotes(self):
        if not self.has_subtitle_file():
            raise Exception("Subtitle of movie {} by id of {} does not exist.".format(self.title1, self.id))
        if Movie.__CASHED_QUOTES.__contains__(self.id):
            return Movie.__CASHED_QUOTES[self.id]
        quotes = get_quotes_of_subtitle(self.get_subtitle_file_path())
        Movie.__CASHED_QUOTES[self.id] = quotes
        return quotes

    def delete_quotes_from_elasticsearch(self):
        with ElasticConnectionFactory.create_new_connection() as es:
            es.delete_by_query(index='quotes', body={"query": {"match": {"movie_id": self.id}}})
            self.is_inserted_in_elasticsearch = False
            self.save()

    def insert_quotes_to_elasticsearch(self):
        with ElasticConnectionFactory.create_new_connection() as es:
            # Delete current inserted quotes
            es.delete_by_query(index='quotes', body={"query": {"match": {"movie_id": self.id}}})

            quotes = self.get_quotes()

            actions = []
            # Create actions to perform on elasticsearch
            for index, quote in enumerate(quotes):
                action = {
                    "_index": "quotes",
                    "_source": {
                        "quote": quote,
                        "movie_id": self.id
                    }
                }
                # Add last quote time and next quote time to sources of each action
                if index != 0:
                    action['_source']['last_quote_time'] = quotes[index - 1]['start_time']
                if index != len(quote) - 1:
                    action['_source']['next_quote_time'] = quotes[index - 1]['end_time']

            # Insert quotes by bulk query
            helpers.bulk(es, actions)
            self.is_inserted_in_elasticsearch = True
            self.save()
