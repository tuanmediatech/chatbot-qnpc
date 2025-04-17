import logging
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import subprocess

# Thiết lập logging để kiểm tra các hoạt động
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Khai báo Flask app và Telegram bot
app = Flask(__name__)
TELEGRAM_TOKEN = "7862312312:AAGRe-kNQPtz2CDmfowFlCAPmJbYUIcJKvgn"  # Thay thế bằng token của bot
bot = Bot(token=TELEGRAM_TOKEN)

# Webhook URL (thay yourdomain.com bằng URL của bạn hoặc URL từ ngrok nếu đang thử nghiệm local)
WEBHOOK_URL = f"https://chatbot-qnpc.onrender.com/{TELEGRAM_TOKEN}"

# Hàm xử lý tin nhắn từ Telegram
def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    
    # Đoạn mã xử lý tin nhắn
    if "lấy" in text and "bài" in text:
        try:
            # Trích xuất số bài viết từ tin nhắn
            so_bai = int(''.join(filter(str.isdigit, text)))
            logger.info(f"Nhận yêu cầu lấy {so_bai} bài viết")

            update.message.reply_text(f"📥 Đã nhận yêu cầu. Đang tiến hành lấy {so_bai} bài viết...")

            # Gọi script xử lý lấy bài viết (giả sử app-web-qnpc-fn.py xử lý)
            subprocess.Popen(["python", "app-web-qnpc-fn.py", str(so_bai)])

            update.message.reply_text(
                "✅ Đang xử lý... Vui lòng đợi khoảng 30–60 giây.\n"
                "📄 Kết quả sẽ có trên Google Sheets:\n"
                "🔗 https://docs.google.com/spreadsheets/d/11eUWnFjsHTpHX81Ap6idXd-SDhzO1pCOQ0NNOptYxv8/edit?gid=907517028#gid=907517028"
            )

        except ValueError:
            update.message.reply_text("⚠️ Không rõ số bài viết bạn muốn lấy. Vui lòng thử lại như: *lấy 5 bài viết*", parse_mode="Markdown")
        except Exception as e:
            logger.error(f"Lỗi trong xử lý: {str(e)}")
            update.message.reply_text("⚠️ Đã xảy ra lỗi. Vui lòng thử lại sau.")
    else:
        update.message.reply_text("👋 Nhắn: *lấy 5 bài viết* để bắt đầu.", parse_mode="Markdown")

# Route chính để kiểm tra Flask server hoạt động
@app.route('/', methods=['GET'])
def index():
    logger.info("Flask Server is Running!")  # Log khi Flask đang chạy
    return "✅ Flask Server is Running!"

# Webhook route xử lý POST từ Telegram
@app.route('/' + TELEGRAM_TOKEN, methods=['POST'])
def webhook():
    json_str = request.get_data(as_text=True)
    update = Update.de_json(json_str, bot)
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    dispatcher = application.dispatcher
    dispatcher.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    try:
        dispatcher.process_update(update)
        logger.info("Đã xử lý webhook thành công.")
    except Exception as e:
        logger.error(f"Lỗi khi xử lý webhook: {str(e)}")

    return 'ok'

if __name__ == "__main__":
    # Chạy Flask app
    app.run(port=5000, debug=True)
