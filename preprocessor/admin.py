from django.contrib import admin

from preprocessor.models import PreprocessingMovie


@admin.action(description="Restart preprocess task")
def restart_preprocess_of_movie(admin_model, request, queryset):
    for preprocess in queryset.all():
        preprocess.state = PreprocessingMovie.IN_QUEUE
        preprocess.downloading_trys = 0
        preprocess.converting_trys = 0
        preprocess.save()


class PreprocessorAdmin(admin.ModelAdmin):
    actions = [restart_preprocess_of_movie]
    list_display = ('id', 'movie', 'state')
    list_filter = ['state']
    ordering = ['id']
    readonly_fields = ['state', 'downloading_trys', 'converting_trys']


admin.site.register(PreprocessingMovie, PreprocessorAdmin)
