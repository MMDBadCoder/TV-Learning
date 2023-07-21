from django.contrib import admin

from movies_manager.models import Movie


@admin.action(description="Insert text to elasticsearch")
def insert_text_to_elasticsearch(admin_model, request, queryset):
    for movie in queryset.all():
        movie.insert_text_to_elasticsearch()


class MovieAdmin(admin.ModelAdmin):
    actions = [insert_text_to_elasticsearch]

    list_display = ('id', 'title1', 'genre', 'imdb_rating')
    list_filter = ('hidden_to_users', 'is_inserted_in_elasticsearch')
    search_fields = ['title1']
    ordering = ['id']


admin.site.register(Movie, MovieAdmin)
