import csv
from django.core.management.base import BaseCommand
from film.models import Media
from faker import Faker
from pathlib import Path
from tqdm import tqdm
import random, sys


csv.field_size_limit(sys.maxsize)


class Command(BaseCommand):
    help = "Импорт названий фильмов с русскими названиями из IMDb akas"

    def handle(self, *args, **kwargs):
        akas_path = Path('title.akas.tsv')
        basics_path = Path('title.basics.tsv')
        fake = Faker()

        self.stdout.write("📥 Загрузка русских названий из title.akas.tsv...")

        # 1. Загружаем только ru названия
        rus_titles = {}
        with open(akas_path, encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')
            for row in tqdm(reader, desc="Импорт ru названий"):
                if row['language'] == 'ru' and row['title'] and row['isOriginalTitle'] == '0':
                    rus_titles[row['titleId']] = row['title']

        self.stdout.write(f"✅ Найдено русских названий: {len(rus_titles)}")

        # 2. Загружаем основные данные
        count = 0
        self.stdout.write("📦 Импортируем фильмы и сериалы из title.basics.tsv...")
        with open(basics_path, encoding='utf-8') as f:
            reader = list(csv.DictReader(f, delimiter='\t'))
            for row in tqdm(reader, desc="Импорт media"):
                title_id = row['tconst']
                if title_id not in rus_titles:
                    continue

                if row['titleType'] not in ['movie', 'tvSeries']:
                    continue

                title = rus_titles[title_id]
                media_type = 'movie' if row['titleType'] == 'movie' else 'series'
                year = row['startYear']
                if year == '\\N':
                    year = None

                Media.objects.create(
                    name=title,
                    type=media_type,
                    release_date=f"{year}-01-01" if year else None,
                    hash=fake.unique.lexify(text='????????????'),
                )
                count += 1

        self.stdout.write(self.style.SUCCESS(f"🎉 Успешно импортировано {count} фильмов/сериалов"))