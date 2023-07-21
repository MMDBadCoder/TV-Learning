from django.db import models


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

    def insert_text_to_elasticsearch(self):
        pass
