from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Media, Actor, Director


class MediaSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9
    limit = 10000

    def items(self):
        return Media.objects.filter(blocked=False).order_by('id')

    def location(self, item):
        return item.get_absolute_url()

    def lastmod(self, obj):
        return obj.updated
class ActorSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6
    limit = 10000

    def items(self):
        return Actor.objects.filter(characters__isnull=False).distinct().order_by('id')

    def location(self, item):
        return item.get_absolute_url()
    def lastmod(self, obj):
        return obj.updated
class DirectorSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6
    limit = 10000

    def items(self):
        return Director.objects.filter(media__isnull=False).order_by('id')

    def location(self, item):
        return item.get_absolute_url()
    def lastmod(self, obj):
        return obj.updated

sitemaps = {
    'medias': MediaSitemap,
    'actors': ActorSitemap,
    'directors': DirectorSitemap,
}
sitemap_medias = {
    'medias': MediaSitemap,
}
sitemap_actors = {
    'actors': ActorSitemap,
}
sitemap_directors = {
    'directors': DirectorSitemap,
}



class HomeSitemap(Sitemap):
    changefreq = "daily"
    priority = 1.0

    def items(self):
        return ['home', 'films', 'series', 'collections']

    def location(self, item):
        return reverse(item)

sitemaps_pages = {
    'home': HomeSitemap,
}