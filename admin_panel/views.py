import os.path

from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseBadRequest
from django.shortcuts import render, redirect

from admin_panel.forms import SubtitleUploadForm
from movies_manager.models import Movie


@login_required
@user_passes_test(lambda u: u.is_superuser)
def play_movie(request, movie_id):
    movie = Movie.objects.get(id=movie_id)
    data = {
        'movie': movie
    }
    return render(request, 'my_admin_pages/play_movie.html', data)


@login_required
@user_passes_test(lambda u: u.is_superuser)
def upload_subtitle_file(request, movie_id):
    form = SubtitleUploadForm(request.POST, request.FILES)
    if not form.is_valid():
        return HttpResponseBadRequest()

    movie = Movie.objects.get(id=movie_id)
    subtitle_file_path = movie.subtitle_file.path
    if os.path.exists(subtitle_file_path):
        os.remove(subtitle_file_path)

    uploaded_subtitle = form.files['subtitle']
    with open(subtitle_file_path, 'wb+') as destination:
        for chunk in uploaded_subtitle.chunks():
            destination.write(chunk)

    movie.reload_all_data_based_on_subtitle()

    return redirect('admin-play-movie', movie_id)
