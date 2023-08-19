from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe
from tqdm import tqdm

from movies_manager.models import Movie
from preprocessor.models import PreprocessingMovie


@admin.action(description="Load to elasticsearch")
def load_quotes_to_elasticsearch(admin_model, request, queryset):
    for movie in tqdm(queryset.all()):
        if movie.subtitle_file:
            movie.insert_quotes_to_elasticsearch()


@admin.action(description="Download & Convert")
def create_preprocess_task_of_movies(admin_model, request, queryset):
    for movie in tqdm(queryset.all()):
        create_preprocess_task(movie)


def create_preprocess_task(movie: Movie):
    if movie.specific_stream_url and \
            not PreprocessingMovie.objects.exclude(state=PreprocessingMovie.SUCCESSFUL).filter(movie=movie).exists():
        PreprocessingMovie(movie=movie, download_url=movie.video_stream_url()).save()


class NonEmptyStreamURLFilter(admin.SimpleListFilter):
    title = 'Having specific stream url'
    parameter_name = 'non_empty_stream_url'

    def lookups(self, request, model_admin):
        return (
            ('non_empty', 'Have specific stream url'),
            ('empty', 'Default stream url'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'non_empty':
            return queryset.exclude(specific_stream_url__exact='')
        elif self.value() == 'empty':
            Movie.objects.filter()
            return queryset.filter(specific_stream_url__exact='')


class MovieAdmin(admin.ModelAdmin):
    actions = [load_quotes_to_elasticsearch, create_preprocess_task_of_movies]

    list_display = ('id', 'title1', 'play_movie_button')
    list_filter = ('visible', NonEmptyStreamURLFilter)
    search_fields = ['id', 'title1']
    ordering = ['id']

    def play_movie_button(self, movie):
        url = reverse('admin-play-movie', args=[movie.id])
        button_html = f'<a class="button" href="{url}">Play</a>'
        return mark_safe(button_html)

    play_movie_button.short_description = 'Watching'


admin.site.register(Movie, MovieAdmin)
