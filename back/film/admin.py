from django.contrib import admin, messages
from django.urls import path
from django.shortcuts import redirect

from .models import *
from .tasks import import_medias as iMedias


# Register your models here.
@admin.register(Actor)
class ActorAdmin(admin.ModelAdmin):
    list_display = ['name', 'country', 'birth_date', 'updated', 'created']
    search_fields = ('name', 'hash')
admin.site.register(Genre)

admin.site.register(Voiceover)

admin.site.register(Country)
admin.site.register(Language)
admin.site.register(ProductionStudio)

# admin.site.register(TypeMedia)

@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    change_list_template = "admin/media_changelist.html"
    
    list_display = ['name', 'episode_progress', 'type', 'views', 'get_countries', 'release_date']
    list_filter = ['country', 'release_date']

    search_fields = (
        'name',
        'inId',
        'hash',
        'original_name',
    )
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("import-medias/", self.admin_site.admin_view(self.import_medias), name="import-medias"),
            path("import-medias-wp/", self.admin_site.admin_view(self.import_medias_wp), name="import-medias-wp"),
        ]
        return custom_urls + urls

    def import_medias(self, request):
        iMedias.delay()
        self.message_user(request, "Импорт запущен через Celery", messages.SUCCESS)
        return redirect("..")
    def import_medias_wp(self, request):
        iMedias.delay(poster=False)
        self.message_user(request, "Импорт запущен через Celery", messages.SUCCESS)
        return redirect("..")
    
    def get_countries(self, obj):
        return ", ".join([c.name for c in obj.country.all()])
    get_countries.short_description = 'Countries'

    def episode_progress(self, obj):
        return obj.get_episode_progress()
    episode_progress.short_description = 'Episode Progress'


admin.site.register(MediaPlayer)
# admin.site.register(MediaVoiceover)
# admin.site.register(Video)
# admin.site.register(VideoView)
# admin.site.register(VideoSource)

admin.site.register(MediaCharacter)
admin.site.register(MediaVote)
admin.site.register(MediaComment)

admin.site.register(Collection)