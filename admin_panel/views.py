from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render

from movies_manager.models import Movie


@login_required
@user_passes_test(lambda u: u.is_superuser)
def play_movie(request, movie_id):
    movie = Movie.objects.get(id=movie_id)
    data = {
        'movie': movie
    }
    return render(request, 'my_admin_pages/play_movie.html', data)
