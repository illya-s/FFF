from django.urls import path
from . import api_views


urlpatterns = [
    path("csrf/", api_views.get_csrf),
    # path('user_info/', api_views.user_info),
    path('lr-request-code/', api_views.lr_request_code),
    path('lr-enter-code/', api_views.lr_enter_code),
    path('logout/', api_views.logout_view),
    
    path('is-auth/', api_views.IsAuth.as_view()),
    
    path('session/', api_views.UserSessionView.as_view(), name='api-session'),
    path('session/list/', api_views.UserSessionListView.as_view()),
    path('session/kill/<str:session_key>/', api_views.KillSessionView.as_view()),
    path('session/kill/user/', api_views.KillUserSessionsView.as_view()),
    path('session/kill/all/', api_views.KillAllSessions.as_view()),
    
    path("media_status/<str:status_type>/", api_views.MediaStatusListView.as_view()),
]