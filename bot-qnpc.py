import os
import asyncio
from flask import Flask, request
import telegram
from telegram import Update
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters, CallbackContext

# Khởi tạo Flask app
app = Flask(__name__)

# Khai báo BOT TOKEN
BOT_TOKEN = "7862312312:AAGRe-kNQPtz2CDmfowFlCAPmJbYUIcJKvg"
bot = telegram.Bot(token=BOT_TOKEN)

# Tạo dispatcher để xử lý các message và command
dispatcher = Dispatcher(bot, None, workers=0)

# Hàm gửi tin nhắn (async)
async def send_reply(chat_id, message_text):
    await bot.send_message(chat_id=chat_id, text=f"Bạn vừa gửi: {message_text}")

# Route webhook phải TRÙNG với BOT_TOKEN
@app.route(f'/{BOT_TOKEN}', methods=['POST'])
def webhook():
    # Lấy dữ liệu Telegram gửi tới
    update = telegram.Update.de_json(request.get_json(force=True), bot)

    # Xử lý nội dung tin nhắn
    if update.message:
        chat_id = update.message.chat.id
        message_text = update.message.text

        # Gửi lại tin nhắn
        asyncio.run(send_reply(chat_id, message_text))

    return 'ok', 200

# Route kiểm tra server sống
@app.route('/', methods=['GET'])
def index():
    return 'Bot đang hoạt động! 🚀', 200

# Main app
if __name__ == "__main__":
    # Lắng nghe Webhook và chạy Flask app
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
