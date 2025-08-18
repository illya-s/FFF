from django.urls import path
from django.views.generic.base import RedirectView
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('films/', views.films, name='films'),
    path('series/', views.series, name='series'),
    path('collections/', views.collections, name='collections'),
    path('collection/<str:hash>/', views.collection, name='collect'),
    
    path('director/<str:hash>/', views.director, name='director'),
    path('actor/<str:hash>/', views.actor, name='actor'),

    path('random_media/', views.random_media, name='random_media'),

    path('search/', views.media_search, name='media_search'),
    path('autocomplete/', views.media_autocomplete, name='media_autocomplete'),

    path("watch/<str:hash>/", views.media_get, name="media"),
    path("watch/<str:hash>/comment/", views.media_post, name="media_comment"),
    # path('video/<str:hash>/', views.stream_video, name='stream_video'),

    path('tul/<str:hash>/', views.toggle_user_list, name='toggle_user_list'),
    path('grade/<str:hash>/', views.grade, name='grade'),

    path('.well-known/traffic-advice', views.traffic_advice),
    path('kodik.txt', views.serve_file),
    path("robots.txt", views.robots_txt, name="robots_txt"),
    path('favicon.ico', views.favicon_view),
]

from .sitemaps import sitemaps, sitemap_medias, sitemap_actors, sitemap_directors, sitemaps_pages

urlpatterns += [
    path('sitemap-directors.xml', views.mSitemap, {'sitemaps': sitemap_directors}, name='sitemap_directors'),
    path('sitemap-actors.xml', views.mSitemap, {'sitemaps': sitemap_actors}, name='sitemap_actors'),
    path('sitemap-medias.xml', views.mSitemap, {'sitemaps': sitemap_medias}, name='sitemap_medias'),

    path('sitemap-<section>-<int:page>.xml', views.mSitemapSection, {'sitemaps': sitemaps}, name='sitemap-section-page'),

    path('sitemap-pages.xml', views.mSitemapSection, {'sitemaps': sitemaps_pages}, name='sitemap-pages'),
]
