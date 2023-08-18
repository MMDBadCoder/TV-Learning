from django.db import models


class SubtitleUpload(models.Model):
    file = models.FileField(upload_to='subtitle_files/', blank=True)
