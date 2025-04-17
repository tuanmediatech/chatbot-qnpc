import logging
import subprocess
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Bật log
logging.basicConfig(level=logging.INFO)

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

# Hàm khởi động bot
if __name__ == '__main__':
    TELEGRAM_TOKEN = "7862312312:AAGRe-kNQPtz2CDmfowFlCAPmJbYUIcJKvg"  # ✅ Thay bằng token thật của bạn

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    print("🤖 Bot đã khởi chạy thành công!")
    app.run_polling()
