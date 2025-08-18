from django.urls import path
from . import api_views


urlpatterns = [
    path('legal/', api_views.LegalView.as_view()),
    path('support/', api_views.SupportRequestCreateView.as_view()),
]