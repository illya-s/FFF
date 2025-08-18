from __future__ import absolute_import, unicode_literals
import os
from kombu import Queue, Exchange
# import backup.tasks

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FF.settings')

app = Celery('FF')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.timezone = 'Europe/Kyiv'

app.conf.update(
    broker_url='redis://localhost:6379/0',
    broker_connection_retry_on_startup=True,
)

CELERY_TASK_QUEUES = (
    Queue('hard', Exchange('hard'), routing_key='hard'),
    Queue('fast', Exchange('fast'), routing_key='fast'),
)

# CELERY_TASK_ROUTES = {
#     'FF.tasks.task_for_worker1': {'queue': 'queue1'},
#     'FF.tasks.task_for_worker2': {'queue': 'queue2'},
# }

app.autodiscover_tasks()


# app.conf.beat_schedule = {}

app.conf.beat_schedule = {
    'import-medias-daily': {
        'task': 'film.tasks.import_medias',
        'schedule': crontab(hour=3, minute=15),
    },
    'import-genres-monthly': {
        'task': 'film.tasks.get_genres',
        'schedule': crontab(day_of_month=1, hour=2, minute=15),
    },
}