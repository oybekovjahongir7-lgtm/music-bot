import logging
import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
import yt_dlp
import re

BOT_TOKEN = os.getenv("BOT_TOKEN", "8816584321:AAG7goREJmlxSnWB9MSKap8qVnp9gdaNOmA")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

user_state = {}
user_playlists = {}

def search_music(query: str, max_results: int = 5):
    ydl_opts = {'quiet': True, 'no_warnings': True, 'extract_flat': True, 'default_search': 'ytsearch', 'noplaylist': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(f"ytsearch{max_results}:{query}", download=False)
        if result and 'entries' in result:
            return result['entries']
    return []

def download_audio(url: str, output_path: str = "/tmp"):
    ydl_opts = {'format': 'bestaudio/best', 'outtmpl': f'{output_path}/%(title)s.%(ext)s', 'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}], 'quiet': True, 'no_warnings': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        title = info.get('title', 'audio')
        filename = ydl.prepare_filename(info).rsplit('.', 1)[0] + '.mp3'
        return filename, title

def format_duration(seconds):
    if not seconds: return "?"
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"

@dp.mess
