from django.urls import path
from . import views

app_name = 'social'

urlpatterns = [
    path('', views.index, name='social'),

    path('api/list/', views.api_list, name='api_list'),
]