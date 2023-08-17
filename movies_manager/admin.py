from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe
from tqdm import tqdm

from movies_manager.models import Movie


@admin.action(description="Insert quotes to elasticsearch")
def insert_quotes_to_elasticsearch(admin_model, request, queryset):
    for movie in tqdm(queryset.all()):
        movie.insert_quotes_to_elasticsearch()


@admin.action(description="Delete quotes from elasticsearch")
def delete_quotes_from_elasticsearch(admin_model, request, queryset):
    for movie in tqdm(queryset.all()):
        movie.delete_quotes_from_elasticsearch()


class MovieAdmin(admin.ModelAdmin):
    actions = [insert_quotes_to_elasticsearch, delete_quotes_from_elasticsearch]

    list_display = ('id', 'title1', 'genre', 'imdb_rating', 'play_movie_button')
    list_filter = ('visible', 'is_inserted_in_elasticsearch')
    search_fields = ['title1']
    ordering = ['id']

    def play_movie_button(self, movie):
        url = reverse('admin-play-movie', args=[movie.id])
        button_html = f'<a class="button" href="{url}">Play</a>'
        return mark_safe(button_html)

    play_movie_button.short_description = 'Play video'


admin.site.register(Movie, MovieAdmin)
