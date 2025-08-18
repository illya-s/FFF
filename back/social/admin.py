from django.contrib import admin
from .models import SocialNetwork

@admin.register(SocialNetwork)
class SocialNetworkAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'is_active', 'order')
    list_editable = ('is_active', 'order')