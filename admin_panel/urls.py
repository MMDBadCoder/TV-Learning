from django.urls import path
from . import views

urlpatterns = [
    path('play-movie/<int:movie_id>', views.play_movie, name='admin-play-movie')
]
