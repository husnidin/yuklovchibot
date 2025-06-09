import os
import requests
from yt_dlp import YoutubeDL
from telegram import Update, InputFile
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters
)
from telegram.request import HTTPXRequest


# Telegram bot token
# @yukla_007_bot
# BOT_TOKEN = '7213944408:AAF2Kx2CksHwiFsHQYfxRU4_MHN_6OwAGJ0'

# @yuklab_ol_media_bot
BOT_TOKEN = '7804783035:AAE9RSyD-DeUS_KYlvBWqlvup7DoqI0EVbs'

# Video yoki musiqa yuklab olish funksiyasi
def download_media(url):
    try:
        ydl_opts = {
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'format': 'best',
        }
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            return ydl.prepare_filename(info)
    except Exception as e:
        print(f"Xatolik: {e}")
        return None

# URL orqali rasm yuklash
def download_image(url):
    try:
        response = requests.get(url)
        content_type = response.headers['Content-Type']
        ext = content_type.split('/')[-1]
        filename = f"downloads/image.{ext}"
        with open(filename, 'wb') as f:
            f.write(response.content)
        return filename
    except Exception as e:
        print(f"Xatolik (rasm): {e}")
        return None

# Botga xabar kelganda ishlovchi handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    await update.message.reply_text("Yuklab olinmoqda, iltimos kuting...")

    if "youtube.com" in url or "youtu.be" in url or "tiktok.com" in url:
        file_path = download_media(url)
    elif url.endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
        file_path = download_image(url)
    else:
        file_path = download_media(url)

    if file_path and os.path.exists(file_path):
        try:
            with open(file_path, 'rb') as f:
                file = InputFile(f, filename=os.path.basename(file_path))

                if file_path.endswith(('.mp4', '.mkv', '.webm')):
                    await update.message.reply_video(file)
                elif file_path.endswith(('.mp3', '.wav', '.ogg')):
                    await update.message.reply_audio(file)
                elif file_path.endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                    await update.message.reply_photo(file)
                else:
                    await update.message.reply_document(file)
        except Exception as e:
            await update.message.reply_text(f"Yuborishda xatolik: {e}")
        finally:
            os.remove(file_path)
    else:
        await update.message.reply_text("Faylni yuklab bo'lmadi. URL to'g'riligini tekshiring.")

# Bot ishga tushirish
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("URL yuboring va men faylni sizga yuboraman!")

def main():
    if not os.path.exists("downloads"):
        os.makedirs("downloads")

    # So‘rovlar uchun timeoutni to‘g‘ri usulda beramiz
    from httpx import Timeout
    timeout = Timeout(timeout=30.0)
    request = HTTPXRequest()

    app = ApplicationBuilder().token(BOT_TOKEN).request(request).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot ishga tushdi...")
    app.run_polling()


if __name__ == "__main__":
    main()
