
from django.db.models.functions import TruncDate, TruncHour
from django.db.models import Count
from django.utils import timezone
from django_celery_beat.models import PeriodicTask, CrontabSchedule

from .models import VisitLog, VisitLogType

import datetime
from calendar import monthrange
from croniter import croniter


def get_hourly_counts(log_type=None):
    now = timezone.now()
    start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)

    qs = VisitLog.objects.filter(timestamp__range=(start_time, now))

    if log_type == 'home':
        qs = qs.filter(path='/')
    elif log_type:
        qs = qs.filter(type=VisitLogType.objects.get_or_create(name=log_type)[0])

    exclude_list = [
        VisitLogType.objects.get_or_create(name='admin')[0],
        VisitLogType.objects.get_or_create(name='statify')[0],
        VisitLogType.objects.get_or_create(name='static')[0],
        VisitLogType.objects.get_or_create(name='media')[0]
    ]

    return {
        entry['hour'].hour: entry['count']
        for entry in (
            qs.exclude(type__in=exclude_list)
              .annotate(hour=TruncHour('timestamp'))
              .values('hour')
              .annotate(count=Count('id'))
        )
    }

def get_daily_counts(log_type=None):
    today = datetime.datetime.now().date()
    year = today.year
    month = today.month

    days_in_month = monthrange(year, month)[1]
    start_date = datetime.date(year, month, 1)
    end_date = datetime.date(year, month, days_in_month)

    qs = VisitLog.objects.filter(timestamp__date__range=(start_date, end_date))
    if log_type == 'home':
        qs = qs.filter(path='/')
    elif log_type:
        qs = qs.filter(type=VisitLogType.objects.get_or_create(name=log_type)[0])

    exclude_list = [
        VisitLogType.objects.get_or_create(name='admin')[0],
        VisitLogType.objects.get_or_create(name='statify')[0],
        VisitLogType.objects.get_or_create(name='static')[0],
        VisitLogType.objects.get_or_create(name='media')[0]
    ]

    return {
        entry['day']: entry['count']
        for entry in (
            qs.exclude(type__in=exclude_list)
                .annotate(day=TruncDate('timestamp'))
                .values('day')
                .annotate(count=Count('id'))
        )
    }

def get_next_import_time():
    from datetime import datetime

    base_time = timezone.now()
    cron = croniter("15 3 * * *", base_time)  # соответствует crontab(hour=3, minute=15)
    return cron.get_next(datetime)