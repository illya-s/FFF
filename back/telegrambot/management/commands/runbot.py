from django.core.management.base import BaseCommand
from telegrambot.bot import main

class Command(BaseCommand):
    help = "Запуск Telegram-бота"

    def handle(self, *args, **options):
        main()