from django.contrib.sessions.models import Session
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.utils import timezone

from .models import LoginCode

import random, config
import geoip2.database
from user_agents import parse


User = get_user_model()
GEOIP_DB_PATH  = 'geoip/GeoLite2-Country.mmdb'

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def get_ip_info(ip):
    reader = geoip2.database.Reader(GEOIP_DB_PATH)

    try:
        response = reader.city(ip)
        city = response.city.name or "Unknown"
        country = response.country.iso_code or "Unknown"
        return f"{city} ({country})"
    except:
        return "Unknown"

def get_os_info(ua_string):
    user_agent = parse(ua_string)
    os_name = user_agent.os.family
    os_version = '.'.join(str(v) for v in user_agent.os.version if v is not None)

    return f"{os_name} {os_version}"

def generate_and_send_login_code(user):
    code = f"{random.randint(100000, 999999)}"
    LoginCode.objects.create(user=user, code=code)

    send_mail(
        "Ваш код для входа",
        f"Ваш код: {code}",
        config.EMAIL,
        [user.email],
    )

def get_user_sessions(request):
    sessions = Session.objects.filter(expire_date__gte=timezone.now())
    current = []
    others = []

    for session in sessions:
        data = session.get_decoded()

        if str(request.user.id) == str(data.get('_auth_user_id')):
            session_info = {
                'session_key': session.session_key,
                'expire_date': session.expire_date.isoformat(),
                'ip_info': get_ip_info(data.get("ip")),
                'os_info': get_os_info(data.get("user_agent")),
                'isCurrent': session.session_key == request.session.session_key
            }
            if session.session_key == request.session.session_key:
                current.append(session_info)
            else:
                others.append(session_info)

    return current + others

def delete_user_session(user, session_key):
    """
    Удаляет конкретную сессию пользователя по session_key.
    Возвращает True, если сессия была удалена, False если не найдена.
    """
    try:
        session = Session.objects.get(session_key=session_key)
        data = session.get_decoded()
        if str(data.get('_auth_user_id')) == str(user.id):
            session.delete()
            return True
    except Session.DoesNotExist:
        pass

    return False