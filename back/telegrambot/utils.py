from telegram import Bot

import os, config, asyncio


def send_channel_message(video_url: str = None, text: str = '', parse_mode: str = "HTML"):
    asyncio.run(_send_channel_message(video_url, text, parse_mode))

async def _send_channel_message(video_url, text, parse_mode):
    """
    Отправляет видео с подписью в Telegram-канал.

    :param video_url: Ссылка на видео (URL или путь к файлу)
    :param caption: Подпись к видео
    :param parse_mode: HTML или Markdown
    """

    bot = Bot(token=os.getenv("TBOT_KEY"))
    chat_id = config.CHAT_ID

    if video_url and not config.DEBUG:
        await bot.send_video(chat_id=chat_id, video=video_url, caption=text, parse_mode=parse_mode)
    else:
        await bot.send_message(chat_id=chat_id, text=text, parse_mode=parse_mode)
