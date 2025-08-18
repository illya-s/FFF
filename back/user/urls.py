from django.urls import path
from . import views, api_views

from django.views.generic.base import RedirectView
from django.urls import reverse_lazy


urlpatterns = [
    path('lr/', views.lr_request_code, name='lr_request_code'),
    path('lr/code/', views.lr_enter_code, name='lr_enter_code'),

    path('logout/', views.log_out, name='logout'),

    path('profile/', views.profile, name='profile'),
    path('history/', views.watching, name='watching'),
    path('rated/', views.rated, name='rated'),

    path('change-username/', views.change_username, name='change_username'),
    path('change-password/', views.change_password, name='change_password'),

    path('favorites/', views.favorite_media, name='favorite_media'),
    path('watching/', views.watching_media, name='watching_media'),
    path('later/', views.watch_later_media, name='watch_later_media'),
    path('bookmarks/', views.bookmarks_media, name='bookmarks_media'),
    path('dropped/', views.dropped_media, name='dropped_media'),

    path('user_agreement/', RedirectView.as_view(url=reverse_lazy('legal'), permanent=True)),
    path('privacy_policy/', RedirectView.as_view(url=reverse_lazy('legal'), permanent=True)),
]
