import os
import asyncio
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import logging

# Khởi tạo Flask app và Bot
app = Flask(__name__)
TELEGRAM_TOKEN = "7862312312:AAGRe-kNQPtz2CDmfowFlCAPmJbYUIcJKvgn"
bot = Bot(token=TELEGRAM_TOKEN)

# Webhook URL
WEBHOOK_URL = f"https://chatbot-qnpc.onrender.com/{TELEGRAM_TOKEN}"

# Hàm set webhook
async def set_webhook():
    await bot.set_webhook(url=WEBHOOK_URL)

# Hàm xử lý tin nhắn
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ...

# Định nghĩa các routes
@app.route('/', methods=['GET'])
def index():
    return "✅ Flask Server is Running!"

@app.route('/' + TELEGRAM_TOKEN, methods=['POST'])
def webhook():
    ...

# Gọi webhook 1 lần khi app khởi động
@app.before_first_request
def before_first_request_func():
    asyncio.run(set_webhook())

# **Không cần if __name__ == "__main__": nữa!!**
