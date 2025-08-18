from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

from django.shortcuts import redirect
from django.views.generic import RedirectView

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView


urlpatterns = [
    path('admin/', admin.site.urls),
    path("ckeditor5/", include('django_ckeditor_5.urls')),
    path('accounts/', include('allauth.socialaccount.providers.google.urls')),

    path('', include('film.urls')),
    path('u/', include('user.urls')),
    path('statify/', include('statify.urls')),
    path('statify/social/', include('social.urls')),
    path('tb/', include('telegrambot.urls')),
    path('support/', include('support.urls')),

    path('api/', include('support.api_urls')),
    path('api/', include('film.api_urls')),
    path('api/', include('user.api_urls')),
    
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/docs/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)