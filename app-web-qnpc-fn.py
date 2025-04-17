import os
import json
import logging
import subprocess
from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import Application, MessageHandler, ContextTypes, filters

# Cấu hình logging
logging.basicConfig(level=logging.INFO)

# Tạo Flask app
app = Flask(__name__)

# Đọc TELEGRAM_TOKEN từ biến môi trường
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_SECRET_PATH = "/webhook"

# Khởi tạo Telegram bot app
telegram_app = Application.builder().token(TELEGRAM_TOKEN).build()

# Xử lý tin nhắn Telegram
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    
    if "lấy" in text and "bài" in text:
        try:
            so_bai = int(''.join(filter(str.isdigit, text)))

            await update.message.reply_text(f"📥 Đã nhận yêu cầu. Đang tiến hành lấy {so_bai} bài viết...")

            # Chạy subprocess file xử lý
            subprocess.Popen(["python", "xu-ly-lay-bai.py", str(so_bai)])

            await update.message.reply_text(
                "✅ Đang xử lý... Vui lòng đợi 30–60 giây.\n"
                "📄 Kết quả sẽ có trên Google Sheets:\n"
                "🔗 https://docs.google.com/spreadsheets/d/11eUWnFjsHTpHX81Ap6idXd-SDhzO1pCOQ0NNOptYxv8/edit?gid=907517028#gid=907517028"
            )
        except ValueError:
            await update.message.reply_text(
                "⚠️ Không rõ số bài viết bạn muốn lấy. Hãy nhắn như: *lấy 5 bài viết*", parse_mode="Markdown")
        except Exception as e:
            logging.error(f"Lỗi khi xử lý lấy bài: {e}")
            await update.message.reply_text("⚠️ Đã xảy ra lỗi. Vui lòng thử lại sau.")
    else:
        await update.message.reply_text(
            "👋 Gửi tin nhắn: *lấy 5 bài viết* để bắt đầu.", parse_mode="Markdown"
        )

# Gắn handler cho bot
telegram_app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

# Route kiểm tra server sống
@app.route('/', methods=['GET'])
def index():
    return "✅ Flask Server is Running!"

# Route webhook Telegram
@app.route(WEBHOOK_SECRET_PATH, methods=['POST'])
def webhook():
    try:
        update = Update.de_json(request.get_json(force=True), telegram_app.bot)
        telegram_app.update_queue.put_nowait(update)
    except Exception as e:
        logging.error(f"Webhook error: {e}")
    return jsonify({"status": "ok"})

# Set webhook khi server start
async def set_webhook():
    webhook_url = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}{WEBHOOK_SECRET_PATH}"
    await telegram_app.bot.set_webhook(webhook_url)
    logging.info(f"Webhook set: {webhook_url}")

if __name__ == "__main__":
    import asyncio

    asyncio.run(set_webhook())

    app.run(host="0.0.0.0", port=5000)
