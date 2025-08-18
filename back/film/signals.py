from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache

from .models import Media

@receiver([post_save, post_delete], sender=Media)
def clear_media_search_cache(sender, **kwargs):
    cache.clear()
