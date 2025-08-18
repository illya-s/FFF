from django.utils.decorators import method_decorator
from django.utils import timezone
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from django.http import JsonResponse
from film.utils import get_api_media_list
from .utils import delete_user_session, generate_and_send_login_code, get_ip_info, get_os_info, get_user_sessions, get_client_ip
from .models import LoginCode
from django.contrib.auth import get_user_model, login, logout
from django.contrib import messages
from django.contrib.sessions.models import Session

from django.middleware.csrf import get_token

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from auth import json_login_required


User = get_user_model()

def get_csrf(request):
    response = JsonResponse({'detail': 'CSRF cookie set'})
    response['X-CSRFToken'] = get_token(request)
    return response

@csrf_protect
def lr_request_code(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Только POST разрешен'}, status=405)

    email = request.POST.get('email')
    if not email:
        return JsonResponse({'error': 'Введите email'}, status=400)

    user, created = User.objects.get_or_create(email=email, defaults={'username': email.split('@')[0]})

    try:
        generate_and_send_login_code(user)
        request.session['user_id_for_code'] = user.id
        return JsonResponse({'success': True, 'message': 'Код отправлен на email'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_protect
def lr_enter_code(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Только POST разрешен'}, status=405)

    user_id = request.session.get('user_id_for_code')
    if not user_id:
        return JsonResponse({'error': 'Сначала запросите код'}, status=400)

    code = request.POST.get('code')
    if not code:
        return JsonResponse({'error': 'Введите код'}, status=400)

    code_obj = LoginCode.objects.filter(user_id=user_id, code=code, is_used=False).first()

    if code_obj and not code_obj.is_expired():
        code_obj.is_used = True
        code_obj.save()

        user = code_obj.user
        user.is_active = True
        user.save()

        login(request, user, backend='allauth.account.auth_backends.AuthenticationBackend')

        request.session['ip'] = get_client_ip(request)
        request.session['user_agent'] = request.META.get('HTTP_USER_AGENT', '')
        
        return JsonResponse({'success': True, 'message': 'Вы вошли', 'user': {
            'id': user.id,
            'email': user.email,
            'username': user.username,
            'avatar': user.avatar.url if user.avatar else None
        }})

    return JsonResponse({'error': 'Неверный или просроченный код'}, status=400)

def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        return JsonResponse({'detail': 'Вы успешно вышли'})
    else:
        return JsonResponse({'detail': 'Вы уже вышли'})

class IsAuth(APIView):
    def get(self, request):
        return Response({'is_auth': request.user.is_authenticated})

@method_decorator(ensure_csrf_cookie, name='dispatch')
class UserSessionView(APIView):
    def get(self, request):
        if not request.user.is_authenticated:
            return Response({'isAuthenticated': False})

        user = request.user

        return Response({
            'isAuthenticated': True,
            'id': user.id,
            'email': user.email,
            'username': user.username,
            'avatar': user.avatar.url if user.avatar else None,
            'joined': user.date_joined.isoformat(),
            'session': {
                'session_key': request.session.session_key,
                'ip_info': get_ip_info(request.session.get('ip', request.META.get('REMOTE_ADDR'))),
                'os_info': get_os_info(request.session.get('user_agent', request.META.get('HTTP_USER_AGENT', '')))
            }
        })

# @json_login_required
# def user_info(request):
#     return JsonResponse({
#         'id': request.user.id,
#         'email': request.user.email,
#         'username': request.user.username,
#         'avatar': request.user.avatar.url if request.user.avatar else None,
#         'joined': request.user.date_joined
#     })

class UserSessionListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({'list': get_user_sessions(request)})

class KillSessionView(APIView):
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, session_key):
        if not session_key:
            return Response({'error': 'Не указан session_key'}, status=400)
        elif session_key == request.session.session_key:
            return Response({'error': 'Нельзя завершить текущую сессию'}, status=400)

        deleted = delete_user_session(request.user, session_key)

        if deleted:
            return Response({'success': True, 'message': 'Сессия удалена'})
        else:
            return Response({'success': False, 'message': 'Сессия не найдена'})

class KillUserSessionsView(APIView):
    permission_classes = [IsAuthenticated]
    
    def delete(self, request):
        user = request.user
        currentSession = request.session
        sessions = Session.objects.filter(expire_date__gte=timezone.now())
        count = 0

        for session in sessions:
            data = session.get_decoded()
            if str(data.get('_auth_user_id')) == str(user.id) and session.session_key != currentSession.session_key:
                session.delete()
                count += 1

        return Response({'success': True, 'message': f'Сессии пользователя завершены: {count}'})

class KillAllSessions(APIView):
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        sessions = Session.objects.all()
        sessions.delete()
        
        return Response({'detail': 'Сессии успешно завершены'})


class MediaStatusListView(APIView):
    permission_classes = [IsAuthenticated]

    STATUS_MAP = {
        "favorites": "favorites",
        "watching": "watching",
        "watch_later": "later",
        "bookmarks": "bookmarks",
        "dropped": "dropped",
    }

    def get(self, request, status_type):
        if status_type not in self.STATUS_MAP:
            return Response({"error": "Invalid status type"}, status=400)

        page = int(request.GET.get("page", 1))

        related_name = self.STATUS_MAP[status_type]
        items = getattr(request.user, related_name).all()
        objs = [item.media for item in items]

        data = get_api_media_list(25, page, objs)

        return Response(data)