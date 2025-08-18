from celery import shared_task

from .models import VideoStat

from django.db.models import F, Count

import datetime
from django.utils import timezone


@shared_task(queue='fast')
def increment_media_view(hash, session_key):
    from .models import VisitLog
    from film.models import Media

    if not session_key:
        return False

    try:
        media = Media.objects.get(hash=hash)
    except Media.DoesNotExist:
        return False
    one_hour_ago = timezone.now() - datetime.timedelta(hours=1)

    already_viewed = VisitLog.objects.filter(
        media=media,
        session_key=session_key,
        timestamp__gte=one_hour_ago
    ).exists()

    if not already_viewed:
        Media.objects.filter(pk=media.pk).update(views=F('views') + 1)
        return True
    return False


@shared_task(queue='fast')
def log_visit_async(data):
    from .models import VisitLog
    VisitLog.objects.create(**data)

@shared_task(queue='hard')
def update_video_stats():
    from .models import VisitLog
    views = VisitLog.objects.all()

    for item in views:
        count = item.media.views

        stat, isCreated = VideoStat.objects.get_or_create(media_id=item.media.pk)
        if isCreated:
            stat.media = item.media
        stat.views_count = count
        stat.save()