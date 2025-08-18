from django.urls import path
from django.conf.urls import handler400, handler403, handler404, handler500
from . import views

urlpatterns = [
    path("", views.SupportRequestView.as_view(), name="support"),
    path("success/", views.SupportRequestView.as_view(), name="support_success"),

    path("copyright/", views.CopyrightRequestView.as_view(), name="copyright"),
    path("copyright/success/", views.CopyrightRequestView.as_view(), name="copyright_success"),

    path("copyright/<int:pk>/response/", views.CopyrightResponseView.as_view(), name="copyright_response"),
    path("404", views.test404),

    path('legal/', views.legal, name='legal'),
]


handler400 = 'support.views.bad_request'
handler403 = 'support.views.permission_denied'
handler404 = 'support.views.page_not_found'
handler500 = 'support.views.server_error'