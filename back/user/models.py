from django.db import models
from django.utils import timezone
from django.utils.timezone import now
from django.utils.text import slugify
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django_prometheus.models import ExportModelOperationsMixin

from django.conf import settings

import os, uuid


def generate_unique_hash():
    return uuid.uuid4().hex[:12]


def user_upload_to(instance, filename):
    username = slugify(instance.username) or 'user'
    ff = f'{username}_{generate_unique_hash()}'
    filename = f"avatar.{filename.split('.')[-1]}"
    return os.path.join("user", ff, filename)
class UserProfile(ExportModelOperationsMixin("dataset"), AbstractUser):
    avatar = models.ImageField(upload_to=user_upload_to, blank=True, null=True)
    email = models.EmailField(unique=True)

    REQUIRED_FIELDS = ['email']
    USERNAME_FIELD = 'username'
    
    def __str__(self):
        return self.username


class LoginCode(ExportModelOperationsMixin("dataset"), models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def is_expired(self):
        return timezone.now() > self.created_at + timezone.timedelta(minutes=5)

    def __str__(self):
        return f"{self.user.email} - {self.code}"


class LoginSession(ExportModelOperationsMixin("dataset"), models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='loginSessions')

    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)

    session_key = models.CharField(max_length=40, null=True, blank=True)

    login_time = models.DateTimeField(default=now)


class FavoriteMedia(ExportModelOperationsMixin("dataset"), models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True, related_name='favorites')
    media = models.ForeignKey('film.Media', on_delete=models.CASCADE, blank=True, null=True, related_name='favorites')

    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.media.name}"
    class Meta:
        unique_together = ('user', 'media')

class WatchingMedia(ExportModelOperationsMixin("dataset"), models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True, related_name='watching')
    media = models.ForeignKey('film.Media', on_delete=models.CASCADE, blank=True, null=True, related_name='watching')

    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.media.name}"
    class Meta:
        unique_together = ('user', 'media')

class WatchLaterMedia(ExportModelOperationsMixin("dataset"), models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True, related_name='later')
    media = models.ForeignKey('film.Media', on_delete=models.CASCADE, blank=True, null=True, related_name='later')

    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.media.name}"
    class Meta:
        unique_together = ('user', 'media')

class BookmarksMedia(ExportModelOperationsMixin("dataset"), models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True, related_name='bookmarks')
    media = models.ForeignKey('film.Media', on_delete=models.CASCADE, blank=True, null=True, related_name='bookmarks')

    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.media.name}"
    class Meta:
        unique_together = ('user', 'media')

class DroppedMedia(ExportModelOperationsMixin("dataset"), models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True, related_name='dropped')
    media = models.ForeignKey('film.Media', on_delete=models.CASCADE, blank=True, null=True, related_name='dropped')

    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.media.name}"
    class Meta:
        unique_together = ('user', 'media')

