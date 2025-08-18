from django.urls import path
from . import views

urlpatterns = [
    path('', views.statify, name='statify'),
    path('log/', views.visitlog, name='visitlog'),
    path('log/list/', views.visitlog_list, name='visitlog_list'),
    path('log/<int:pk>/', views.visitlog_detail, name='visitlog_detail'),

    path('import/', views.import_list, name='import_list'),
    path('import/<int:pk>/', views.import_detail, name='import_detail'),

    path('support_requests/', views.support_request_list, name='support_requests'),
    # path('errors/<int:pk>/', views.media_import_error_detail, name='media_import_error_detail'),

    path('logs/visit/', views.media_logs, name='logs_by_month'),
    path('logs/media/', views.media_views_by_month, name='media_views_by_month'),
]