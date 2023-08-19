import os

from django.db import models
from elasticsearch import helpers

from TV_LEARNING.settings import NGINX_URL, MEDIA_ROOT, BASE_DIR
from common_utils.elasticsearch import ElasticConnectionFactory
from common_utils.subtitle_utils import get_quotes_of_subtitle, generate_vtt_file


class Movie(models.Model):
    __CASHED_QUOTES = {}

    title1 = models.CharField(max_length=100, blank=False, null=False)
    title2 = models.CharField(max_length=100, blank=False, null=False)
    genre = models.CharField(max_length=100, blank=True, null=False, default='')
    votes_count = models.IntegerField(blank=False, null=False)
    imdb_rating = models.FloatField(blank=False, null=False)
    visible = models.BooleanField(default=False, blank=False, null=False)
    is_inserted_in_elasticsearch = models.BooleanField(default=False, blank=False, null=False)
    specific_stream_url = models.CharField(max_length=1000, blank=True, null=False, default='')
    subtitle_file = models.FileField(upload_to='subtitle_files/', blank=True, null=True)

    def __str__(self):
        return '-'.join([str(self.id), self.title1])

    def video_stream_url(self):
        if self.specific_stream_url:
            return self.specific_stream_url
        return f'{NGINX_URL}{self.id}.mp4'

    def get_subtitle_file_path(self):
        return os.path.join(BASE_DIR, MEDIA_ROOT, self.subtitle_file.url)

    def try_to_generate_vtt_file(self, force_to_regenerate=False):
        subtitle_file_path = self.subtitle_file.path
        vtt_file_path = subtitle_file_path.replace('subtitle_files', 'static/web-subtitles').replace('.srt', '.vtt')
        if not os.path.isfile(vtt_file_path) or force_to_regenerate:
            generate_vtt_file(self.subtitle_file.path, vtt_file_path)

    def get_quotes(self):
        if not self.subtitle_file:
            raise Exception("Subtitle of movie {} by id of {} does not exist.".format(self.title1, self.id))
        if Movie.__CASHED_QUOTES.__contains__(self.id):
            return Movie.__CASHED_QUOTES[self.id]
        quotes = get_quotes_of_subtitle(self.subtitle_file.path)
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
            self.delete_quotes_from_elasticsearch()

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
                if index < len(quotes) - 1:
                    action['_source']['next_quote_time'] = quotes[index + 1]['end_time']
                actions.append(action)

            # Insert quotes by bulk query
            helpers.bulk(es, actions)
            self.is_inserted_in_elasticsearch = True
            self.save()

    def reload_all_data_based_on_subtitle(self):
        self.try_to_generate_vtt_file(True)
        self.insert_quotes_to_elasticsearch()
