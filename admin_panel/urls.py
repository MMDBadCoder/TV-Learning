from django.urls import path
from . import views

urlpatterns = [
    path('play-movie/<int:movie_id>', views.play_movie, name='admin-play-movie'),
    path('upload-subtitle/<int:movie_id>', views.upload_subtitle_file, name='admin-upload-subtitle'),
]
