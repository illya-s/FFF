from django.db.models.signals import post_save, pre_save, m2m_changed
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone

from .models import Post
from .utils import send_channel_message


@receiver(pre_save, sender=Post)
def generate_uid(sender, instance, **kwargs):
    if not instance.uid:
        year = timezone.now().year
        prefix = f"SD_{year}_"

        last_instance = Post.objects.filter(uid__startswith=prefix).order_by('-uid').first()

        if last_instance:
            try:
                last_number = int(last_instance.uid.split('-')[-1])
            except ValueError:
                last_number = 0
        else:
            last_number = 0

        next_number = str(last_number + 1).zfill(6)
        instance.uid = f"{prefix}{next_number}"

@receiver(m2m_changed, sender=Post.media.through)
def post_created_handler(sender, instance, action, **kwargs):
    if action == 'post_add':
        print(f"Создан пост: {instance.uid}")

        text = instance.get_telegram_text()
        send_channel_message(text=text)