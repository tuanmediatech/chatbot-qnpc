import logging
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import os

# Bật log
logging.basicConfig(level=logging.INFO)

# Flask app setup
app = Flask(__name__)

# Khai báo Bot và Token
TELEGRAM_TOKEN = "7862312312:AAGRe-kNQPtz2CDmfowFlCAPmJbYUIcJKvg"  # ✅ Thay bằng token thật của bạn
bot = Bot(token=TELEGRAM_TOKEN)

# Cài đặt Webhook URL
WEBHOOK_URL = "https://yourdomain.com/" + TELEGRAM_TOKEN  # Thay 'yourdomain.com' bằng URL thực tế của bạn
bot.set_webhook(url=WEBHOOK_URL)

# Hàm xử lý tin nhắn từ người dùng
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    
    if "lấy" in text and "bài" in text:
        try:
            # Trích xuất số bài viết từ tin nhắn
            so_bai = int(''.join(filter(str.isdigit, text)))
            
            await update.message.reply_text(f"📥 Đã nhận yêu cầu. Đang tiến hành lấy {so_bai} bài viết...")

            # Chạy script xử lý lấy bài viết ở chế độ nền
            subprocess.Popen(["python", "app-web-qnpc-fn.py", str(so_bai)])

            await update.message.reply_text(
                "✅ Đang xử lý... Vui lòng đợi khoảng 30–60 giây.\n"
                "📄 Kết quả sẽ có trên Google Sheets:\n"
                "🔗 https://docs.google.com/spreadsheets/d/11eUWnFjsHTpHX81Ap6idXd-SDhzO1pCOQ0NNOptYxv8/edit?gid=907517028#gid=907517028"
            )

        except ValueError:
            await update.message.reply_text("⚠️ Không rõ số bài viết bạn muốn lấy. Vui lòng thử lại như: *lấy 5 bài viết*", parse_mode="Markdown")
        except Exception as e:
            logging.error(f"Lỗi trong xử lý: {str(e)}")
            await update.message.reply_text("⚠️ Đã xảy ra lỗi. Vui lòng thử lại sau.")
    else:
        await update.message.reply_text("👋 Nhắn: *lấy 5 bài viết* để bắt đầu.", parse_mode="Markdown")

# Flask route để xử lý webhook
@app.route('/' + TELEGRAM_TOKEN, methods=['POST'])
def webhook():
    json_str = request.get_data(as_text=True)
    update = Update.de_json(json_str, bot)
    
    # Xử lý update từ Telegram
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    dispatcher = application.dispatcher
    dispatcher.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    # Xử lý cập nhật
    dispatcher.process_update(update)
    return 'ok'

# Chạy Flask app
if __name__ == "__main__":
    app.run(port=5000)
