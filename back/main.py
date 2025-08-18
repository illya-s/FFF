import os
import django

# Установить настройки Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FF.settings')  # замените на имя своего проекта
django.setup()

from film.tasks import *
from film.models import Media, Country, Genre, Voiceover
from statify.models import VisitLog, VisitLogType

from django.core.mail import send_mail
from additional import is_email

from urllib.parse import urlparse
from tqdm import tqdm

import sys, subprocess

args = sys.argv[1:]

if "--self-update" in args:
    subprocess.run(["sh", "load.sh"])

if "--load-countries" in args:
    get_countries.delay()
if "--load-genres" in args:
    get_genres.delay()
if "--load-voiceovers" in args:
    get_voiceovers.delay()

if "--remove-countries" in args:
    Country.objects.all().delete()
if "--remove-genres" in args:
    Genre.objects.all().delete()
if "--remove-voiceovers" in args:
    Voiceover.objects.all().delete()


if "--update-logs" in args:
    for log in tqdm(VisitLog.objects.all(), desc="Process", colour="green", ascii=[" ", "-"], bar_format=f"{{desc}} {{bar:{100}}} | {{n_fmt}}/{{total_fmt}}"):
        path = urlparse(log.path).path
        parts = [p for p in path.split('/') if p]
        
        if log.path.startswith(('/admin/', '/statify/', '/kodik.txt')):
            log.delete()
        elif parts:
            if log.path == '/':
                type_name = 'home'
            else:
                parts = log.path.strip('/').split('/')
                type_name = parts[0] if parts and parts[0] else 'unknown'

            log_type, _ = VisitLogType.objects.get_or_create(name=type_name)
            log.type = log_type
            log.save()

if "--remove-media" in args:
    try:
        MediaPlayer.objects.all().delete()
        Media.objects.all().delete()

        print("✅ Media deleted successfully.")
    except Exception as e:
        print("Error:")
        print(e)

if "--test-mail" in args:
    index = args.index('--test-mail')

    if index + 1 < len(args):
        value = args[index + 1]
    if is_email(value):
        send_mail(
            'Hello from Django',
            'This is a test message',
            'noreply@sarangdorama.com',
            [value, 'ilaa64536@gmail.com']
        )
        print("✅ test-mail: mail sent.")
    else:
        print(f"❌ test-mail Error: '{value}' is not")