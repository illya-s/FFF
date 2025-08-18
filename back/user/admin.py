from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(WatchingMedia)
admin.site.register(WatchLaterMedia)
admin.site.register(FavoriteMedia)
admin.site.register(BookmarksMedia)
admin.site.register(DroppedMedia)

class UserProfileAdmin(admin.ModelAdmin):
    search_fields = ('user__username',)

admin.site.register(UserProfile, UserProfileAdmin)