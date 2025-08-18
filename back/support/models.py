from django.db import models
from django_ckeditor_5.fields import CKEditor5Field
from .data import clean_html

# Create your models here.

class Legal(models.Model):
    terms_of_service = CKEditor5Field(config_name='default', help_text="Пользовательское соглашение")
    privacy_policy = CKEditor5Field(config_name='default', help_text="Политика конфиденциальности")

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Legal documents"
    
    def save(self, *args, **kwargs):
        self.terms_of_service = clean_html(self.terms_of_service)
        self.privacy_policy = clean_html(self.privacy_policy)
        super().save(*args, **kwargs)

class CopyrightRequest(models.Model):
    company = models.CharField("Компания", max_length=255, blank=True)
    full_name = models.CharField("Контактное лицо", max_length=255)
    email = models.EmailField("Email")

    message = models.TextField("Сообщение")

    links_to_remove = models.TextField(
        "Прямые ссылки на страницы ресурса, информация с которых подлежит удалению",
        help_text="Укажите одну или несколько ссылок, каждую с новой строки"
    )
    proof_document_url = models.URLField(
        "Ссылка на документ, подтверждающий исключительные права",
        help_text="Укажите ссылку на официальный документ (Google Drive, Dropbox и т.п.)"
    )
    takedown_explanation_text = models.TextField(
        "Текст объяснения для пользователей",
        help_text="Этот текст будет отображаться пользователям на месте удалённого контента"
    )

    attachment = models.FileField("Приложение", upload_to="copyright_attachments/", blank=True, null=True)

    created = models.DateTimeField("Дата отправки", auto_now_add=True)

    class Meta:
        verbose_name = "Запрос от правообладателя"
        verbose_name_plural = "Запросы от правообладателей"

    def __str__(self):
        return f"{self.full_name} ({self.email})"

class CopyrightResponse(models.Model):
    request = models.OneToOneField(CopyrightRequest, on_delete=models.CASCADE, related_name='response', verbose_name="Запрос правообладателя")
    response_text = models.TextField("Текст ответа")
    created_at = models.DateTimeField("Дата ответа", auto_now_add=True)
    is_sent = models.BooleanField("Ответ отправлен правообладателю", default=False)

    class Meta:
        verbose_name = "Ответ на запрос правообладателя"
        verbose_name_plural = "Ответы на запросы правообладателей"

    def __str__(self):
        return f"Ответ на запрос от {self.request.full_name}"



class SupportRequest(models.Model):
    SUBJECT_CHOICES = [
        ("general", "Общие вопросы"),
        ("playback", "Проблемы с воспроизведением видео"),
        ("error", "Сообщить об ошибке"),
        ("partnership", "Сотрудничество"),
        ("ads", "Реклама на сайте"),
        ("copyright", "Жалоба от правообладателя"),
        ("account", "Проблемы с аккаунтом"),
        ("comment", "Жалоба на коментарий"),
        ("other", "Другое"),
    ]

    full_name = models.CharField("Имя", max_length=255)
    email = models.EmailField("Email")

    subject = models.CharField("Тема обращения", max_length=50, choices=SUBJECT_CHOICES)

    message = models.TextField("Сообщение")

    created = models.DateTimeField("Дата отправки", auto_now_add=True)

    class Meta:
        verbose_name = "Обращение в поддержку"
        verbose_name_plural = "Обращения в поддержку"

    def __str__(self):
        return f"{self.get_subject_display()} — {self.full_name}"