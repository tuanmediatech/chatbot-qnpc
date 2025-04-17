import os
import asyncio
import logging
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# Cấu hình logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Khởi tạo Flask app và Telegram bot
app = Flask(__name__)
TELEGRAM_TOKEN = "7862312312:AAGRe-kNQPtz2CDmfowFlCAPmJbYUIcJKvgn"
bot = Bot(token=TELEGRAM_TOKEN)

# Webhook URL
WEBHOOK_URL = f"https://chatbot-qnpc.onrender.com/{TELEGRAM_TOKEN}"

# Hàm set webhook
async def set_webhook():
    await bot.set_webhook(url=WEBHOOK_URL)
    logger.info(f"✅ Webhook set thành công: {WEBHOOK_URL}")

# Hàm xử lý tin nhắn Telegram
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    
    if "lấy" in text and "bài" in text:
        try:
            so_bai = int(''.join(filter(str.isdigit, text)))
            logger.info(f"Nhận yêu cầu lấy {so_bai} bài viết")

            await update.message.reply_text(f"📥 Đã nhận yêu cầu. Đang lấy {so_bai} bài...")

            # Gọi script xử lý lấy bài viết
            # subprocess.Popen(["python", "app-web-qnpc-fn.py", str(so_bai)])  # Bỏ ghi chú nếu có script riêng

            await update.message.reply_text(
                "✅ Đang xử lý...\n"
                "📄 Kết quả sẽ có trên Google Sheets:\n"
                "🔗 https://docs.google.com/spreadsheets/d/11eUWnFjsHTpHX81Ap6idXd-SDhzO1pCOQ0NNOptYxv8/edit?gid=907517028#gid=907517028"
            )

        except ValueError:
            await update.message.reply_text(
                "⚠️ Không rõ số bài viết. Hãy gửi tin nhắn như: *lấy 5 bài viết*",
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.error(f"Lỗi: {e}")
            await update.message.reply_text("⚠️ Đã xảy ra lỗi. Vui lòng thử lại sau.")
    else:
        await update.message.reply_text("👋 Gửi: *lấy 5 bài viết* để bắt đầu.", parse_mode="Markdown")

# Route kiểm tra server sống
@app.route('/', methods=['GET'])
def index():
    return "✅ Server is running!"

# Route nhận webhook từ Telegram
@app.route(f'/{TELEGRAM_TOKEN}', methods=['POST'])
def webhook():
    json_str = request.get_data(as_text=True)
    update = Update.de_json(json_str, bot)

    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    dispatcher = application.dispatcher
    dispatcher.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    try:
        dispatcher.process_update(update)
        logger.info("✅ Đã xử lý webhook thành công.")
    except Exception as e:
        logger.error(f"Lỗi khi xử lý webhook: {e}")

    return 'ok'

# Route để set webhook thủ công
@app.route('/set_webhook', methods=['GET'])
def setup_webhook():
    asyncio.run(set_webhook())
    return "✅ Webhook đã được thiết lập thành công!"
