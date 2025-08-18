from django.urls import path
from django.views.generic.base import RedirectView
from . import api_views


urlpatterns = [
    path('top-genres/', api_views.TopGenresView.as_view(), name='top-genres'),
    path('top-media/', api_views.TopMediaView.as_view(), name='top-media'),
    path('filters/', api_views.FiltersView.as_view(), name='filters'),

    path('watch/<str:hash>/', api_views.MediaView.as_view()),

    path('list/', api_views.ListView.as_view()),
    # path('collections/', api_views.collections, name='collections'),

    path('search/list/', api_views.SearchMediaView.as_view(), name='api_media_search'),
    path('search/auto/', api_views.SearchAutocompleteMediaView.as_view()),
]