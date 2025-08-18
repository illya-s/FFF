from django.db import models
from django.utils.html import strip_tags
from django.urls import reverse
from django_prometheus.models import ExportModelOperationsMixin

from film.models import Media

import os, config


# Create your models here.
def short_upload_to(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"short.{ext}"

    return os.path.join("shorts", instance.uid, filename)


class Post(ExportModelOperationsMixin("dataset"), models.Model):
    uid = models.CharField(max_length=20, unique=True, blank=True, help_text="Уникальный ID для поиска")

    media = models.ManyToManyField(Media, related_name='posts', verbose_name="Медиа")
    short = models.FileField(upload_to=short_upload_to, null=True, blank=True, verbose_name="Вертикальное видео (Short)")

    created = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f"Пост {self.uid}"

    def get_telegram_text(self):
        from django.contrib.sites.models import Site
        current_site = Site.objects.get_current()
        domain = current_site.domain

        tLines = []

        if self.media.all().count() == 1:
            media = self.media.first()
            hashtags = ['#SarangDorama', f'#{media.release_date.year}', f'#{self.uid}']

            tLines.append(f'📺 {media.name}')
            my = media.release_date.strftime('%d.%m.%Y')
            tLines.append(f'📅 <b>Год:</b> {my}')
            if media.episodes_aired and media.episodes_total:
                tLines.append(f'🎞 <b>Серий:</b> {media.get_episode_progress()}')

            if media.country:
                cl = [country.name for country in media.country.all()]
                hashtags.append(' '.join([f'#{name.replace(' ', '_')}' for name in cl]))
                tLines.append(f'🌏 <b>Страна:</b> {', '.join(cl)}')

            if media.genres:
                gl = [genre.name for genre in media.genres.all()]
                hashtags.append(' '.join([f'#{name.replace(' ', '_')}' for name in gl]))
                tLines.append(f'🎭 <b>Жанры:</b> {', '.join(gl)}')

            if media.description_modified:
                tLines.append(f'📝 <b>Описание:</b> ')

            if config.DEBUG == True:
                url = f"http://{domain}{reverse('media', kwargs={'hash': media.hash})}"
                urlLine = f'<a href="{url}">{url}</a>'
            else:
                url = f"https://{domain}{reverse('media', kwargs={'hash': media.hash})}"
                urlLine = f'<a href="{url}">{url}</a>'

            tLines.append(f'🔗 <b>Смотреть:</b> {urlLine}')

            tLines.append(' '.join(hashtags))
        return '\n\n'.join(tLines)