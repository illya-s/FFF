from django.db import models
from django.contrib.auth import get_user_model
from django_prometheus.models import ExportModelOperationsMixin

from film.models import *

class VisitLogType(ExportModelOperationsMixin("dataset"), models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class VisitLog(ExportModelOperationsMixin("dataset"), models.Model):
    type = models.ForeignKey('VisitLogType', on_delete=models.CASCADE, null=True, verbose_name="Тип визита", help_text="Категория визита (например, обычный, API-запрос и т.д.)")
    path = models.CharField(max_length=255, verbose_name="Путь", help_text="URL-путь, по которому был выполнен запрос")
    method = models.CharField(max_length=10, verbose_name="Метод", help_text="HTTP-метод запроса (GET, POST и т.п.)")
    protocol = models.CharField(max_length=10, blank=True, default='HTTP/1.1', verbose_name="Протокол", help_text="Версия HTTP-протокола (например, HTTP/1.1)")
    status_code = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="HTTP статус", help_text="Код HTTP-ответа (например, 200, 404)")
    user = models.ForeignKey(get_user_model(), null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Пользователь", help_text="Аутентифицированный пользователь, если есть")
    ip = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP адрес", help_text="IP-адрес клиента")
    country = models.CharField(max_length=2, null=True, blank=True, verbose_name="Код страны", help_text="Двухбуквенный код страны посетителя по IP")
    user_agent = models.TextField(null=True, blank=True, verbose_name="User Agent", help_text="Строка user-agent клиента")
    session_key = models.CharField(max_length=40, null=True, blank=True)
    description = models.TextField(null=True, blank=True, verbose_name="Описание", help_text="Дополнительная информация или комментарии к логу")

    media = models.ForeignKey(Media, null=True, blank=True, on_delete=models.SET_NULL, related_name="visit_logs")

    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Дата и время", help_text="Время посещения")

    class Meta:
        verbose_name = "Лог посещения"
        verbose_name_plural = "Логи посещений"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=["path", "session_key", "timestamp", "media"]),
        ]

    def __str__(self):
        return f"[{self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] {self.method} {self.path} {self.status_code} ({self.ip})"

class VideoStat(ExportModelOperationsMixin("dataset"), models.Model):
    media = models.OneToOneField(Media, on_delete=models.CASCADE, related_name='stats')
    views_count = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return f"{self.media.name} — {self.views_count}"


class MediaImportLog(ExportModelOperationsMixin("dataset"), models.Model):
    is_load_all = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def created_count(self):
        return self.entries.filter(action=MediaImportLogEntry.Action.CREATED).count()

    def updated_count(self):
        return self.entries.filter(action=MediaImportLogEntry.Action.UPDATED).count()

    def skipped_count(self):
        return self.entries.filter(action=MediaImportLogEntry.Action.SKIPPED).count()

    def error_count(self):
        return self.entries.filter(action=MediaImportLogEntry.Action.MEDIA_ERROR).count()

    def loaded_count(self):
        return self.created_count() + self.updated_count() + self.skipped_count() + self.error_count()

    def total_count(self):
        total = self.total.first()
        return total.q if total else 0


class MediaImportLogEntry(ExportModelOperationsMixin("dataset"), models.Model):
    class Action(models.TextChoices):
        INFO    = 'info', 'Info'
        CREATED = 'created', 'Created'
        UPDATED = 'updated', 'Updated'
        SKIPPED = 'skipped', 'Skipped'
        MEDIA_ERROR = 'media_error', 'MediaError'
        ERROR = 'error', 'Error'

    log = models.ForeignKey(MediaImportLog, on_delete=models.CASCADE, related_name='entries')
    media = models.ForeignKey(Media, null=True, blank=True, on_delete=models.SET_NULL)
    action = models.CharField(max_length=15, choices=Action.choices)
    message = models.TextField(blank=True)

class MediaImportLogTotal(ExportModelOperationsMixin("dataset"), models.Model):
    log = models.ForeignKey(MediaImportLog, on_delete=models.CASCADE, related_name='total')
    q = models.PositiveIntegerField(default=0)
    temp = models.CharField(max_length=255, null=True, blank=True)

#         TOTAL = 'total', 'Total'

class MediaImportError(ExportModelOperationsMixin("dataset"), models.Model):
    media_id = models.CharField(max_length=255, blank=True, null=True, help_text="ID из API, если есть")
    title = models.TextField(blank=True, null=True, help_text="Название медиа из API")
    error_type = models.CharField(max_length=100, help_text="Тип ошибки: parsing, saving, network, etc.")
    message = models.TextField(help_text="Описание ошибки")
    raw_data = models.JSONField(blank=True, null=True, help_text="Исходный ответ/медиа-объект, если нужно")

    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"[{self.timestamp}] {self.error_type}: {self.message[:50]}"