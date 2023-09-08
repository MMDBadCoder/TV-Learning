from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from elasticsearch import helpers

from TV_LEARNING.settings import NGINX_URL
from common_utils.elasticsearch import ElasticConnectionFactory, validate_existence_of_elasticsearch_index
from movies_manager.utils import get_subtitle_path, prepare_subtitle_file, extract_quotes_from_subtitle


class Movie(models.Model):
    title1 = models.CharField(max_length=100, blank=False, null=False)
    title2 = models.CharField(max_length=100, blank=False, null=False)
    genre = models.CharField(max_length=100, blank=True, null=False, default='')
    votes_count = models.IntegerField(blank=False, null=False)
    imdb_rating = models.FloatField(blank=False, null=False)
    visible = models.BooleanField(default=False, blank=False, null=False)
    specific_stream_url = models.CharField(max_length=1000, blank=True, null=False, default='')
    subtitle_file = models.FileField(upload_to=get_subtitle_path, blank=True, null=True)

    def __str__(self):
        return '-'.join([str(self.id), self.title1])

    def video_stream_url(self):
        if self.specific_stream_url:
            return self.specific_stream_url
        return f'{NGINX_URL}{self.id}.mp4'

    def get_quotes(self):
        if not self.subtitle_file:
            raise Exception("Subtitle of movie {} by id of {} does not exist.".format(self.title1, self.id))
        return extract_quotes_from_subtitle(self.subtitle_file.path)

    def delete_quotes_from_elasticsearch(self):
        with ElasticConnectionFactory.create_new_connection() as es:
            es.delete_by_query(index='quotes', body={"query": {"match": {"movie_id": self.id}}})

    def get_elasticsearch_actions_for_bulk(self):
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

        return actions

    def insert_quotes_to_elasticsearch(self):
        # Create index if not exists
        validate_existence_of_elasticsearch_index()
        with ElasticConnectionFactory.create_new_connection() as es:
            # Delete current inserted quotes
            self.delete_quotes_from_elasticsearch()
            # Get actions for inserting quotes to elasticsearch
            actions = self.get_elasticsearch_actions_for_bulk()
            # Insert quotes by bulk query
            helpers.bulk(es, actions)


@receiver(post_save, sender=Movie)
def movie_post_save_handler(sender, instance: Movie, **kwargs):
    if instance.subtitle_file:
        prepare_subtitle_file(instance.subtitle_file.path)
        instance.insert_quotes_to_elasticsearch()
    else:
        instance.delete_quotes_from_elasticsearch()
