from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe
from tqdm import tqdm

from movies_manager.models import Movie
from preprocessor.models import PreprocessingMovie


@admin.action(description="Insert quotes to elasticsearch")
def insert_quotes_to_elasticsearch(admin_model, request, queryset):
    for movie in tqdm(queryset.all()):
        movie.insert_quotes_to_elasticsearch()


@admin.action(description="Delete quotes from elasticsearch")
def delete_quotes_from_elasticsearch(admin_model, request, queryset):
    for movie in tqdm(queryset.all()):
        movie.delete_quotes_from_elasticsearch()


@admin.action(description="Create preprocess task")
def create_preprocess_task_of_movie(admin_model, request, queryset):
    for movie in tqdm(queryset.all()):
        if movie.specific_stream_url:
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
    actions = [insert_quotes_to_elasticsearch, delete_quotes_from_elasticsearch, create_preprocess_task_of_movie]

    list_display = ('id', 'title1', 'genre', 'imdb_rating', 'play_movie_button')
    list_filter = ('visible', 'is_inserted_in_elasticsearch', NonEmptyStreamURLFilter)
    search_fields = ['id', 'title1']
    ordering = ['id']

    def play_movie_button(self, movie):
        url = reverse('admin-play-movie', args=[movie.id])
        button_html = f'<a class="button" href="{url}">Play</a>'
        return mark_safe(button_html)

    play_movie_button.short_description = 'Play video'


admin.site.register(Movie, MovieAdmin)
