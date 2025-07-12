import os
from aiogram import Bot, Dispatcher, executor, types
import logging
import requests
import subprocess

API_TOKEN = "7793678424:AAE2QXy6PGX5HpLtQhAQFTPvN9pW2_rI-x0"
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)

@dp.message_handler()
async def send_movie(message: types.Message):
    try:
        movie_name = message.text.strip()
        await message.reply("🔍 جاري البحث عن الفيلم...")

        search_url = f"https://yts.mx/api/v2/list_movies.json?query_term={movie_name}"
        res = requests.get(search_url).json()

        if res["data"]["movie_count"] == 0:
            await message.reply("❌ لم أجد هذا الفيلم.")
            return

        movie = res["data"]["movies"][0]
        title = movie["title"]
        torrent_url = movie["torrents"][0]["url"]
        quality = movie["torrents"][0]["quality"]

        await message.reply(f"🎬 {title} ({quality})")
        await message.reply("⬇️ جاري التحميل...")

        subprocess.run(["aria2c", torrent_url, "-d", "downloads"], check=True)

        for file in os.listdir("downloads"):
            if file.endswith(".mp4") or file.endswith(".mkv"):
                video_path = os.path.join("downloads", file)
                with open(video_path, 'rb') as video:
                    await bot.send_video(message.chat.id, video, caption=f"🎬 {title} ({quality})")
                os.remove(video_path)
                break
        else:
            await message.reply("⚠️ لم أجد ملف فيديو داخل التورنت.")
    except Exception as e:
        await message.reply("❌ حدث خطأ أثناء التحميل أو الرفع.")
        print(str(e))

WEBHOOK_HOST = os.getenv('WEBHOOK_HOST')  # هنا الرابط من المتغير البيئي
WEBHOOK_PATH = '/webhook'
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

async def on_startup(dp):
    await bot.set_webhook(WEBHOOK_URL)

async def on_shutdown(dp):
    await bot.delete_webhook()

if __name__ == '__main__':
    os.makedirs("downloads", exist_ok=True)
    executor.start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        host="0.0.0.0",
        port=int(os.environ.get('PORT', 8080))
    )
