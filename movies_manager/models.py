from django.db import models


# Create your models here.

class Movie(models.Model):
    title1 = models.CharField(max_length=100, blank=False, null=False)
    title2 = models.CharField(max_length=100, blank=False, null=False)
    votes_count = models.IntegerField(blank=False, null=False)
    imdb_rating = models.FloatField(blank=False, null=False)
    subtitle_download_url = models.CharField(max_length=1_000, blank=True, null=False, default='')
    video_stream_url = models.CharField(max_length=1_000, blank=True, null=False, default='')
    hidden_to_users = models.BooleanField(default=True, blank=False, null=False)
