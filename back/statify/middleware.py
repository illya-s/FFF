import geoip2.database
from datetime import datetime
from django.utils import timezone

from film.models import Media
from .models import VisitLogType
from .tasks import *
from FF.utils import get_client_ip
from FF.metrics_common import Metrics

import traceback, config


GEOIP_DB_PATH  = 'geoip/GeoLite2-Country.mmdb'

BOT_KEYWORDS = ['bot', 'crawl', 'spider', 'slurp', 'archive', 'search']

class VisitLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.geoip_reader = geoip2.database.Reader(GEOIP_DB_PATH)

    def __del__(self):
        self.geoip_reader.close()

    def __call__(self, request):
        error_trace = None
        response = None

        try:
            response = self.get_response(request)
        except Exception as exc:
            error_trace = traceback.format_exc()
            from django.http import HttpResponseServerError
            response = HttpResponseServerError(str(exc))

        if request.path.startswith(('/random_media/', '/kodik.txt')):
            return response

        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        if any(bot_word in user_agent for bot_word in BOT_KEYWORDS):
            return response

        ip = None if config.DEBUG else get_client_ip(request)

        parts, type_name = self.get_log_type(request)

        status_code = response.status_code if response else None

        if not error_trace and status_code and (400 <= status_code < 600):
            error_trace = f"HTTP Error {status_code}"

        if not request.session.session_key:
            request.session.save()
        session_key = request.session.session_key

        media = None
        if type_name == 'watch':
            try:
                if len(parts) <= 1:
                    raise ValueError("Media HASH not specified")
                media = Media.objects.get(hash=parts[1])
            except Media.DoesNotExist:
                error_trace = f"Media with HASH '{parts[1]}' does not exist"
            except ValueError:
                error_trace = traceback.format_exc()

            if (request.method == 'GET' 
                and session_key 
                and media 
                and status_code 
                and status_code < 400 
                and type_name == 'watch'):
                Metrics.media_visits.inc()
                increment_media_view.apply_async(kwargs={
                    'hash': media.hash,
                    'session_key': session_key
                })

        log_data = {
            'type_id': VisitLogType.objects.get_or_create(name=type_name)[0].id,
            'path': request.path,
            'method': request.method,
            'protocol': request.META.get('SERVER_PROTOCOL'),
            'user_id': request.user.id if request.user.is_authenticated else None,
            'ip': ip,
            'country': self.get_country_code(ip),
            'user_agent': request.META.get('HTTP_USER_AGENT'),
            'timestamp': timezone.now().isoformat(),
            'status_code': status_code,
            'description': error_trace,
            'media_id': media.id if media else None,
            'session_key': session_key,
        }
        log_visit_async.apply_async(args=[log_data])

        return response
    def get_log_type(self, request):
        """
        Возвращает tuple:
        - parts: список частей пути
        - type_name: первая часть пути или 'home'
        """
        path = request.path.strip('/')
        
        if not path:
            return [], 'home'
        
        parts = path.split('/')
        type_name = parts[0] if parts[0] else 'unknown'
        return parts, type_name
    def get_country_code(self, ip):
        if not ip:
            return None
        try:
            response = self.geoip_reader.country(ip)
            return response.country.iso_code
        except Exception as e:
            print(f"[GeoIP Error] {ip}: {e}")
            return None