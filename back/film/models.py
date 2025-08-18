from django.db import models
from django.db.models import Sum, Avg
from django.utils import timezone
from django.utils.text import slugify
import os, uuid, datetime
from django.conf import settings
from django.urls import reverse



def generate_unique_hash():
    from django.utils.crypto import get_random_string
    while True:
        new_hash = get_random_string(length=12)
        if not Actor.objects.filter(hash=new_hash).exists():
            return new_hash

# Info models

class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Название жанра")

    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"

class Country(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Название страны")

    load = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Страна"
        verbose_name_plural = "Страны"

class Language(models.Model):
    code = models.CharField(max_length=10, unique=True, verbose_name="Код языка")
    name = models.CharField(max_length=100, verbose_name="Название языка", unique=True)

    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.name


class Voiceover(models.Model):
    hash = models.CharField(max_length=12, null=False, unique=True, editable=False, default=generate_unique_hash)

    name = models.CharField(max_length=255, null=True, verbose_name="Название студии", unique=True)

    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Студия озвучки"
        verbose_name_plural = "Студии озвучки"

class ProductionStudio(models.Model):
    hash = models.CharField(max_length=12, null=False, unique=True, editable=False, default=generate_unique_hash)
    
    name = models.CharField(max_length=255, null=True, verbose_name="Название студии", unique=True)

    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Студия-производитель"
        verbose_name_plural = "Студии-производители"

class Director(models.Model):
    hash = models.CharField(max_length=12, null=False, unique=True, editable=False, default=generate_unique_hash)
    
    name = models.CharField(max_length=255, verbose_name="Имя режиссёра", unique=True)
    photo = models.ImageField(upload_to="actors/", blank=True, null=True, verbose_name="Фото")

    birth_date = models.DateField(null=True, blank=True, verbose_name="Дата рождения")
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True, related_name="directors", verbose_name="Страна")

    bio = models.TextField(null=True, blank=True, verbose_name="Биография")

    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.name
    def get_absolute_url(self):
        return reverse('director', kwargs={'hash': self.hash})

class Actor(models.Model):
    hash = models.CharField(max_length=12, null=False, unique=True, editable=False, default=generate_unique_hash)
    
    name = models.CharField(max_length=255, null=True, verbose_name="Имя актёра", unique=True)
    photo = models.ImageField(upload_to="actors/", blank=True, null=True, verbose_name="Фото")

    birth_date = models.DateField(null=True, blank=True, verbose_name="Дата рождения")
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True, related_name="actors", verbose_name="Страна")

    bio = models.TextField(null=True, blank=True, verbose_name="Биография")

    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.name
    def get_absolute_url(self):
        return reverse('actor', kwargs={'hash': self.hash})

    class Meta:
        verbose_name = "Актёр"
        verbose_name_plural = "Актёры"



# Media tree models

def poster_upload_to(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"poster.{ext}"
    return os.path.join("medias", instance.hash, filename)

# class TypeMedia(models.Model):
#     name = models.CharField(max_length=500, null=True, blank=False, verbose_name="Название")
#     is_series = models.BooleanField(default=False)

#     def __str__(self):
#         return self.name
class StatusMedia(models.Model):
    name = models.CharField(max_length=500, null=True, blank=False, verbose_name="Название")
    is_series = models.BooleanField(default=False)

    def __str__(self):
        return self.name

def format_views(views):
    if views >= 1_000_000:
        return f"{views / 1_000_000:.1f}M"
    elif views >= 1_000:
        return f"{views / 1_000:.1f}K"
    else:
        return str(views)

class Media(models.Model):
    LOAD_TYPE_CHOICES = [
        ('movie', 'Фильм'),
        ('series', 'Сериал'),
    ]
    
    TYPE_CHOICES = [
        ('cartoon', 'cartoon'),
        ('cartoon-serial', 'cartoon-serial'),
        ('anime', 'anime')
    ] + LOAD_TYPE_CHOICES
    STATUS_TYPE = [
        ('anons', 'Анонс'),
        ('ongoing', 'Выходит'),
        ('released', 'Завершон'),
    ]
    VOICE_CHOICES = [
        ('voiceover', 'Озвучка'),
        ('subtitles', 'Субтитры'),
    ]
    
    class MPAA(models.TextChoices):
        G =    'G', 'Для всех возрастов (G)'
        PG =   'PG', 'С родителями желательно (PG)'
        PG13 = 'PG-13', 'До 13 лет нежелательно (PG-13)'
        R =    'R', 'До 17 лет с родителями (R)'
        RP =   'R+', 'Только взрослым (R+)'
        RX =   'Rx', 'Ограничено (Rx)'

    inId = models.CharField(max_length=1000, unique=True, null=True, blank=False)
    hash = models.CharField(max_length=12, unique=True, editable=False, verbose_name="Хеш", default=generate_unique_hash)

    name = models.CharField(max_length=1000, null=True, unique=True, db_index=True, blank=False, verbose_name="Название")
    original_name = models.CharField(max_length=1000, null=True, blank=True, db_index=True, verbose_name="Название (Оригинал)")
    poster = models.ImageField(upload_to=poster_upload_to, null=True, blank=True)
    release_date = models.DateField(null=True, blank=True, db_index=True, verbose_name="Дата выхода")
    # status = models.ForeignKey(StatusMedia, on_delete=models.SET_NULL, null=True, blank=True, related_name='media', verbose_name="Статус")

    director = models.ManyToManyField(Director, related_name="media", blank=True, db_index=True, verbose_name="Режисёр")

    genres = models.ManyToManyField(Genre, related_name="media", db_index=True, blank=True, verbose_name="Жанры")
    country = models.ManyToManyField(Country, related_name="media", db_index=True, blank=True, verbose_name="Страны")

    type = models.CharField(max_length=14, choices=TYPE_CHOICES, db_index=True, default='series', verbose_name="Тип")
    duration = models.PositiveIntegerField(blank=True, default=0, verbose_name="Продолжительность (мин)")

    description = models.TextField(max_length=5000, null=True, blank=True, verbose_name="Описание")
    description_modified = models.TextField(max_length=5000, null=True, db_index=True, blank=True, verbose_name="Описание (изменённое)")

    imdb_rating = models.FloatField(blank=True, null=True, db_index=True, verbose_name="Рейтинг IMDb")
    kinopoisk_rating = models.FloatField(blank=True, null=True, db_index=True, verbose_name="Рейтинг Кинопоиск")
    avg_rating = models.FloatField(default=0, blank=True, db_index=True)

    minimal_age = models.PositiveIntegerField(blank=True, null=True, verbose_name="Возрастные ограничения")
    rating_mpaa = models.CharField(max_length=15, choices=MPAA.choices, null=True, verbose_name="Рейтинг MPAA")

    episodes_aired = models.PositiveIntegerField(blank=True, null=True, verbose_name="Количество уже вышедших эпизодов")
    episodes_total = models.PositiveIntegerField(blank=True, null=True, verbose_name="Количество эпизодов")

    voiceover_type = models.CharField(max_length=10, choices=VOICE_CHOICES, default='subtitles', verbose_name="Тип", help_text="Озвучка / Субтитры")
    voiceovers = models.ManyToManyField(Voiceover, related_name="media", blank=True, verbose_name="Озвучка")

    related = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='related_media', verbose_name="Связанный объект")

    views = models.PositiveIntegerField(default=0)

    lgbt = models.BooleanField(default=False)
    blocked = models.BooleanField(default=False)

    allow_comments = models.BooleanField(default=True)

    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
    def get_episode_progress(self):
        return f"{self.episodes_aired} / {self.episodes_total}"
    def get_grade(self):
        grades = []

        if self.votes.exists():
            avg_vote = self.votes.aggregate(avg_grade=Avg('grade'))['avg_grade']
            if avg_vote is not None:
                grades.append(avg_vote)

        if self.imdb_rating:
            grades.append(self.imdb_rating)

        if self.kinopoisk_rating:
            grades.append(self.kinopoisk_rating)

        if grades:
            avg = sum(grades) / len(grades)
            return f"{avg:.1f}"
        return 0.0

    def update_avg_rating(self):
        self.__class__.objects.filter(pk=self.pk).update(avg_rating=self.get_grade())
    def get_absolute_url(self):
        return reverse('media', kwargs={'hash': self.hash})

class MediaPlayer(models.Model):
    media = models.ForeignKey(Media, on_delete=models.CASCADE, null=True, related_name="players", verbose_name="Фильм/Сериал")
    url = models.URLField(null=True, blank=True, verbose_name="Ссылка на плеер")
    
    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now=True, null=True)
    
    def __str__(self):
        return self.url

class MediaCharacter(models.Model):
    media = models.ForeignKey(Media, on_delete=models.CASCADE, null=True, related_name="characters", verbose_name="Фильм/Сериал")
    actor = models.ForeignKey(Actor, on_delete=models.CASCADE, null=True, related_name="characters", verbose_name="Актёр")

    character_name = models.CharField(max_length=255, null=True, blank=True, verbose_name="Имя персонажа")

    def __str__(self):
        return f"{self.media.name} ({self.actor.name})"

    class Meta:
        verbose_name = "Персонаж"
        verbose_name_plural = "Персонажи"

class MediaComment(models.Model):
    media = models.ForeignKey(Media, on_delete=models.CASCADE, null=True, blank=True, related_name="comments")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name="comments", verbose_name="Автор")

    text = models.TextField(max_length=5000, null=True, verbose_name="Написать отзыв")

    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.media.name}"

class MediaTrailer(models.Model):
    media = models.ForeignKey(Media, on_delete=models.CASCADE, related_name="trailers", verbose_name="Медиа")
    name = models.CharField(max_length=255, verbose_name="Название трейлера")

    url = models.URLField(null=True, blank=True, verbose_name="Ссылка на трейлер")

    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.media.name} - {self.name}"


""" Media statify """
class MediaVote(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, related_name='votes')
    media = models.ForeignKey(Media, on_delete=models.CASCADE, null=True, related_name='votes')

    grade = models.PositiveSmallIntegerField(choices=[(i, str(i)) for i in range(1, 11)], null=True)

    created = models.DateTimeField(auto_now_add=True, null=True)


    def __str__(self):
        return f"{self.user.username} - {self.media.name} - {self.grade}"

    class Meta:
        unique_together = ('user', 'media')

    def save(self, *args, **kwargs):
        if self.pk:
            raise ValueError("Редактирование голосов запрещено!")
        super().save(*args, **kwargs)

# Video tree models
# class MediaVoiceover(models.Model):
#     TYPE_CHOICES = [
#         ('voiceover', 'Озвучка'),
#         ('subtitles', 'Субтитры'),
#     ]
    
#     media = models.ForeignKey(Media, on_delete=models.CASCADE, null=True, related_name="voiceovers")

#     total_episodes = models.PositiveIntegerField(null=True, blank=True, verbose_name="Всего эпизодов")

#     type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='series', verbose_name="Тип", help_text="Озвучка / Субтитры")
#     voiceover = models.ForeignKey(Voiceover, on_delete=models.SET_NULL, null=True, verbose_name="Озвучка")

#     language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True, blank=True, related_name="voiceovers", verbose_name="Язык")

#     def __str__(self):
#         return f"{self.media.name} - {self.voiceover.name}"

#     def get_total_views(self):
#         result = self.videos.aggregate(total_views=Sum("views"))
#         total_views = result["total_views"] or 0 
#         return format_views(total_views)

#     def get_videos_count(self):
#         return self.videos.count()
#     def get_total_videos_count(self):
#         return self.total_episodes or self.get_videos_count()

# class Video(models.Model):
#     hash = models.CharField(max_length=12, unique=True, editable=False, verbose_name="Хеш", default=generate_unique_hash)
#     voiceover = models.ForeignKey(MediaVoiceover, on_delete=models.CASCADE, null=True, related_name="videos", verbose_name="Озвучка")

#     episode_number = models.PositiveIntegerField(null=True, blank=True, verbose_name="Номер эпизода")
#     season_number = models.PositiveIntegerField(null=True, blank=True, verbose_name="Сезон")

#     views = models.PositiveIntegerField(default=0, verbose_name="Просмотры")

#     class Meta:
#         ordering = ['season_number', 'episode_number']

#     def __str__(self):
#         if self.episode_number:
#             return f"{self.voiceover.media.name} - S{self.season_number}E{self.episode_number}"
#         return f"{self.media.name} (Видео)"

#     def increment_views(self, request):
#         from .models import VideoView
        
#         if not request.session.session_key:
#             return False

#         one_hour_ago = timezone.now() - datetime.timedelta(hours=1)

#         recently_viewed = VideoView.objects.filter(
#             video=self,
#             user=request.user,
#             session_key=request.session.session_key,
#             timestamp__gte=one_hour_ago
#         ).exists()

#         if not recently_viewed:
#             VideoView.objects.create(
#                 video=self,
#                 user=request.user,
#                 session_key=request.session.session_key
#             )
#             self.views = len(self.video_views.all())
#             self.save(update_fields=['views'])
#             return True
#         return False

# VIDEO_QUALITY_CHOICES = [
#     ('144p', '144p'), ('240p', '240p'), ('360p', '360p'),
#     ('480p', 'SD (480p)'), ('720p', 'HD (720p)'),
#     ('1080p', 'FHD (1080p)'),
#     ('1440p', '2K (1440p)'),
#     ('2160p', '4K (2160p)'),
# ]


# def video_upload_to(instance, filename):
#     ext = filename.split('.')[-1]
#     filename = f"video_{instance.video.hash}-{instance.quality}.{ext}"
#     return os.path.join("medias", instance.video.voiceover.media.hash, "videos", filename)
# class VideoSource(models.Model):
#     video = models.ForeignKey(Media, on_delete=models.CASCADE, null=True, related_name='sources')

#     file = models.FileField(upload_to=video_upload_to, null=True, blank=True, verbose_name="Видео файл")
#     url = models.URLField(null=True, blank=True, verbose_name="Ссылка на видео")

#     def __str__(self):
#         return f"{self.video.name} - {self.quality}"

#     def is_file(self):
#         return bool(self.file)

#     def is_url(self):
#         return bool(self.url)


# class VideoView(models.Model):
#     video = models.ForeignKey(Video, on_delete=models.CASCADE, null=True, related_name="video_views")
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name="video_views")

#     session_key = models.CharField(max_length=32, null=True, blank=True)
#     timestamp = models.DateTimeField(auto_now_add=True)



    
def collection_upload_to(instance, filename):
    new_filename = f"poster.{filename.split('.')[-1]}"
    return os.path.join("collections", instance.hash, new_filename)

class Collection(models.Model):
    hash = models.CharField(max_length=12, unique=True, editable=False, verbose_name="Хеш", default=generate_unique_hash)

    name = models.CharField("Название подборки", max_length=255)
    description = models.TextField("Описание", blank=True)
    poster = models.ImageField(upload_to=collection_upload_to, null=True)

    medias = models.ManyToManyField(Media, related_name='collections')

    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.name
    def get_total_views(self):
        return self.views.count()
    def increment_views(self, session_key):
        from .models import CollectionView
        
        if not session_key:
            return False

        one_hour_ago = timezone.now() - datetime.timedelta(hours=1)

        recently_viewed = CollectionView.objects.filter(
            collection=self,
            session_key=session_key,
            timestamp__gte=one_hour_ago
        ).exists()

        if not recently_viewed:
            CollectionView.objects.create(collection=self, session_key=session_key)
            self.views = models.F('views') + 1
            self.save(update_fields=['views'])
        return False


class CollectionView(models.Model):
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE, null=True, related_name="views")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name="views")

    session_key = models.CharField(max_length=32, null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        unique_together = ("collection", "user", "session_key")