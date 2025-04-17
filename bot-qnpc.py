import logging
import os
import subprocess
import asyncio
import json
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

# Bật log
logging.basicConfig(level=logging.INFO)

# Flask app setup
app = Flask(__name__)

# Khai báo Token & Webhook
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")  # Nên dùng biến môi trường
WEBHOOK_SECRET = TELEGRAM_TOKEN  # Secret webhook route (dùng luôn token cho đơn giản)
RENDER_EXTERNAL_HOSTNAME = os.getenv("RENDER_EXTERNAL_HOSTNAME")  # Nếu deploy trên Render
if not RENDER_EXTERNAL_HOSTNAME:
    RENDER_EXTERNAL_HOSTNAME = "yourdomain.com"  # Nếu test local
WEBHOOK_URL = f"https://{RENDER_EXTERNAL_HOSTNAME}/{WEBHOOK_SECRET}"

# Tạo Telegram Application
application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
bot = application.bot

# Hàm xử lý tin nhắn
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()

    if "lấy" in text and "bài" in text:
        try:
            # Trích xuất số bài
            so_bai = int(''.join(filter(str.isdigit, text)))
            await update.message.reply_text(f"📥 Đã nhận yêu cầu. Đang tiến hành lấy {so_bai} bài viết...")

            # Chạy script xử lý
            subprocess.Popen(["python", "xu-ly-lay-bai.py", str(so_bai)])

            await update.message.reply_text(
                "✅ Đang xử lý... Vui lòng đợi khoảng 30–60 giây.\n"
                "📄 Kết quả sẽ có trên Google Sheets:\n"
                "🔗 https://docs.google.com/spreadsheets/d/11eUWnFjsHTpHX81Ap6idXd-SDhzO1pCOQ0NNOptYxv8/edit#gid=0"
            )
        except ValueError:
            await update.message.reply_text(
                "⚠️ Không rõ số bài viết bạn muốn lấy. Vui lòng thử lại như: *lấy 5 bài viết*",
                parse_mode="Markdown"
            )
        except Exception as e:
            logging.error(f"Lỗi xử lý yêu cầu: {str(e)}")
            await update.message.reply_text("⚠️ Đã xảy ra lỗi. Vui lòng thử lại sau.")
    else:
        await update.message.reply_text(
            "👋 Nhắn: *lấy 5 bài viết* để bắt đầu.",
            parse_mode="Markdown"
        )

# Gắn handler
application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

# Flask webhook route
@app.route(f"/{WEBHOOK_SECRET}", methods=["POST"])
def webhook():
    try:
        update = Update.de_json(request.get_json(force=True), bot)
        application.update_queue.put_nowait(update)
    except Exception as e:
        logging.error(f"Webhook error: {str(e)}")
    return "ok"

# Hàm set webhook tự động khi start
async def set_webhook():
    await bot.set_webhook(url=WEBHOOK_URL)
    logging.info(f"✅ Webhook đã set: {WEBHOOK_URL}")

# Main
if __name__ == "__main__":
    asyncio.run(set_webhook())
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
