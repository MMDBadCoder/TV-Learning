import os

from django.db import models
from elasticsearch import helpers

from TV_LEARNING.settings import BASE_DIR
from quote_searcher.connection import ConnectionFactory
from subtitle_utils.utils import get_quotes_of_subtitle, generate_vtt_file


# Create your models here.

class Movie(models.Model):
    title1 = models.CharField(max_length=100, blank=False, null=False)
    title2 = models.CharField(max_length=100, blank=False, null=False)
    genre = models.CharField(max_length=100, blank=True, null=False, default='')
    votes_count = models.IntegerField(blank=False, null=False)
    imdb_rating = models.FloatField(blank=False, null=False)
    video_stream_url = models.CharField(max_length=1_000, blank=True, null=False, default='')
    hidden_to_users = models.BooleanField(default=True, blank=False, null=False)
    is_inserted_in_elasticsearch = models.BooleanField(default=False, blank=False, null=False)

    def __str__(self):
        return '-'.join([str(self.id), self.title1])

    def get_subtitle_file_path(self):
        return os.path.join(BASE_DIR, 'subtitle_files', str(self.id) + ".srt")

    def has_subtitle_file(self):
        subtitle_file_path = self.get_subtitle_file_path()
        return os.path.isfile(subtitle_file_path)

    def check_to_generate_vtt_file(self):
        subtitle_file_path = self.get_subtitle_file_path()
        vtt_file_path = subtitle_file_path.replace('subtitle_files', 'static/web-subtitles').replace('.srt', '.vtt')
        if not os.path.isfile(vtt_file_path):
            generate_vtt_file(self.get_subtitle_file_path(), vtt_file_path)

    def get_quotes(self):
        if not self.has_subtitle_file():
            raise Exception("Subtitle of movie {} by id of {} does not exist.".format(self.title1, self.id))
        return get_quotes_of_subtitle(self.get_subtitle_file_path())

    def delete_quotes_from_elasticsearch(self):
        with ConnectionFactory.create_new_connection() as es:
            es.delete_by_query(index='quotes', body={"query": {"match": {"movie_id": self.id}}})
            self.is_inserted_in_elasticsearch = False
            self.save()

    def insert_quotes_to_elasticsearch(self):
        with ConnectionFactory.create_new_connection() as es:
            # Delete current inserted quotes
            es.delete_by_query(index='quotes', body={"query": {"match": {"movie_id": self.id}}})

            # Insert quotes by bulk query
            actions = [
                {
                    "_index": "quotes",
                    "_source": {
                        "quote": quote,
                        "movie_id": self.id
                    }
                }
                for quote in self.get_quotes()
            ]
            helpers.bulk(es, actions)
            self.is_inserted_in_elasticsearch = True
            self.save()
