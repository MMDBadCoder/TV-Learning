from django.contrib import admin

from movies_manager.models import Movie


@admin.action(description="Download subtitle")
def download_subtitle(admin_model, request, queryset):
    for movie in queryset.all():
        movie.download_subtitle()


class MovieAdmin(admin.ModelAdmin):
    actions = [download_subtitle]
    list_filter = ('hidden_to_users', 'title1')


admin.site.register(Movie, MovieAdmin)
