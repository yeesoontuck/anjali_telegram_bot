import threading
from flask import Flask
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, Application, Defaults
from dotenv import load_dotenv
import os

import asyncio

import sys
sys.path.append("telegram-financial-bot")

from telegram_bot import start, handle_message, handle_document, handle_photo
from gemini_response import gemini_response, get_latest_pdf_path
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes


app = Flask(__name__)
# defaults = Defaults(tzinfo=None, disable_web_page_preview=False, allow_sending_without_reply=True)

def run_telegram_bot():
    asyncio.set_event_loop(asyncio.new_event_loop())

    # Load Telegram Bot Token from environment variables 
    load_dotenv(verbose=True)  # Loads variables from .env file
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

    # Create Telegram bot application using the token
    telegram_app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Register handlers for different types of messages
    telegram_app.add_handler(CommandHandler("start", start)) # /start command
    telegram_app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message)) # Text messages except commands
    telegram_app.add_handler(MessageHandler(filters.Document.ALL, handle_document)) # Any file upload
    telegram_app.add_handler(MessageHandler(filters.PHOTO, handle_photo)) # Photos

    print("Bot started...")
    
    # Start polling Telegram for new updates (messages)
    telegram_app.run_polling(stop_signals=None)


@app.route("/")
def index():
    return "Flask app is running!"

if __name__ == "__main__":
    # threading.Thread(target=app.run, kwargs={"debug": True, "use_reloader": False}, daemon=True).start()
    run_telegram_bot()