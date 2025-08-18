from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from django.http import HttpRequest
from django.urls import reverse
from django.test import RequestFactory

from film.models import Media, Actor, Director
from film.api_views import media_search

import os, json
from asgiref.sync import sync_to_async


# Храним текущий "режим поиска" для каждого пользователя
user_states = {}

main_menu = ReplyKeyboardMarkup(
    keyboard=[["Найти", "Помощь"]],
    resize_keyboard=True,
)

search_submenu = ReplyKeyboardMarkup(
    keyboard=[["Дорама", "Актёр", "Режиссёр"], ["Назад"]],
    resize_keyboard=True,
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Главное меню:", reply_markup=main_menu)

async def search_media(query, label):
    request = RequestFactory().get(reverse('api_media_search'), {'q': query, 'page': 1})
    response = await sync_to_async(media_search)(request)

    if response.status_code == 200:
        data = json.loads(response.content.decode('utf-8'))
        results = data['response'][:10]
        if results:
            text = f"🔍 Результаты по запросу: *{query}* ({label}):\n"
            for obj in results:
                text += f"• {obj['name']} (`{obj['url']}`)\n"
        else:
            text = f"Ничего не найдено по запросу: {query}"
    else:
        text = f"Ничего не найдено по запросу: {query}"
    return text
async def search_actor(query, label):
    results = await sync_to_async(list)(Actor.objects.filter(name__icontains=query)[:10])

    if results:
        text = f"🔍 Результаты по запросу: *{query}* ({label}):\n"
        for obj in results:
            text += f"• {obj.name} (`{obj.hash}`)\n"
    else:
        text = f"Ничего не найдено по запросу: {query}"
    return text
async def search_director(query, label):
    results = await sync_to_async(list)(Director.objects.filter(name__icontains=query)[:10])

    if results:
        text = f"🔍 Результаты по запросу: *{query}* ({label}):\n"
        for obj in results:
            text += f"• {obj.name} (`{obj.hash}`)\n"
    else:
        text = f"Ничего не найдено по запросу: {query}"
    return text

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text.strip()
    state = user_states.get(user_id, "MAIN")
    
    if state == "MAIN":
        if text == "Найти":
            user_states[user_id] = "SEARCH_MENU"
            await update.message.reply_text("Выберите категорию поиска:", reply_markup=search_submenu)
        elif text == "Помощь":
            await update.message.reply_text("Это бот для поиска дорам, актёров и режиссёров.")
        else:
            await update.message.reply_text("Пожалуйста, выберите пункт меню.", reply_markup=main_menu)
    elif state == "SEARCH_MENU":
        if text == "Назад":
            user_states[user_id] = "MAIN"
            await update.message.reply_text("Главное меню:", reply_markup=main_menu)
        elif text in ["Дорама", "Актёр", "Режиссёр"]:
            user_states[user_id] = f"SEARCH_{text.upper()}"
            await update.message.reply_text(f"Введите название {text.lower()}а:", reply_markup=ReplyKeyboardRemove())
        else:
            await update.message.reply_text("Пожалуйста, выберите из меню.", reply_markup=search_submenu)
    elif state.startswith("SEARCH_"):
        sf = None
        match state:
            case 'SEARCH_ДОРАМА':
                sf = search_media
            case 'SEARCH_АКТЁР':
                sf = search_actor
            case 'SEARCH_РЕЖИССЁР':
                sf = search_director
            case _:
                sf = None

        if sf:
            query = update.message.text.strip()
            await update.message.reply_text(await sf(query, state[7:].capitalize()), parse_mode='Markdown')
        else:
            await update.message.reply_text("Ошибка состояния.")
        # После поиска возвращаем в главное меню
        user_states[user_id] = "MAIN"
        await update.message.reply_text("Главное меню:", reply_markup=main_menu)


# Главная функция запуска
def main():
    app = ApplicationBuilder().token(os.getenv("TBOT_KEY")).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()