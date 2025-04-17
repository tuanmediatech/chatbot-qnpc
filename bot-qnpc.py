import os
from flask import Flask, request
import telegram

# Khởi tạo Flask app
app = Flask(__name__)

# Khai báo BOT TOKEN
BOT_TOKEN = "7862312312:AAGRe-kNQPtz2CDmfowFlCAPmJbYUIcJKvg"
bot = telegram.Bot(token=BOT_TOKEN)

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
        bot.send_message(chat_id=chat_id, text=f"Bạn vừa gửi: {message_text}")

    return 'ok', 200

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

# Route kiểm tra server sống
@app.route('/', methods=['GET'])
def index():
    return 'Bot đang hoạt động! 🚀', 200

# Main app
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
