import logging
import os

import requests
import validators
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from validators import ValidationError

TOKEN = "6606232936:AAEAmPr78w3exXIZb8LMkBT-8rE7AJ7JCGU"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


async def send_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    image_url = context.args[0]

    # step 1: validate that the link is an url
    if not validators.url(image_url):
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Please enter a valid URL")
    else:
        # step 2: validate that the link leads to a picture
        image_formats = ("image/png", "image/jpeg", "image/jpg", "image/webp",
                         "image/gif", "image/bmp", "image/tiff", "image/svg+xml")
        r = requests.head(image_url)
        if r.headers["content-type"] in image_formats:
            # Create 'images' directory if it doesn't exist
            os.makedirs('images', exist_ok=True)

            image_context = requests.get(image_url).content
            with open('images/' + image_url.split('/')[-1], 'wb') as handler:
                handler.write(image_context)
            await context.bot.send_photo(chat_id=update.effective_chat.id,
                                         photo=open('images/' + image_url.split('/')[-1], 'rb'))
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text="The URL provided does not lead to an image")


async def send_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    video_url = context.args[0]

    # step 1: validate that the link is an url
    if not validators.url(video_url):
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Please enter a valid URL")
    else:
        # Create 'videos' directory if it doesn't exist
        os.makedirs('videos', exist_ok=True)

        ydl_opts = {
            'outtmpl': 'videos/' + "%(id)s.%(ext)s",
            'format_sort': ['res:1080', 'ext:mp4:m4a']
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            vid_id = info.get('id', "placeholder")
            ext = info.get('ext', "placeholder")

        await context.bot.send_video(chat_id=update.effective_chat.id,
                                     video=open('videos/' + f"{vid_id}.{ext}", 'rb'))


async def helper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = "Hello, this is a bot used to download and upload images and videos \n" \
                "If you want to download an image, please use the command /send_image <IMAGE_URL> \n" \
                "If you want to download a video, please use the command /send_video <VIDEO_URL> \n"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=help_text)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")


if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()

    image_url_handler = CommandHandler('send_image', send_image)
    video_url_handler = CommandHandler('send_video', send_video)
    help_handler = CommandHandler('help', helper)
    start_handler = CommandHandler('start', start)

    application.add_handler(start_handler)
    application.add_handler(help_handler)
    application.add_handler(image_url_handler)
    application.add_handler(video_url_handler)

    application.run_polling()
