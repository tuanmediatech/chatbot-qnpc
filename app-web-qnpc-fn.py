from flask import Flask, render_template, request, Response, stream_with_context
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time

app = Flask(__name__, template_folder="templates", static_folder="static")

# Hàm ghi dữ liệu vào Google Sheets
def write_to_google_sheets(data):
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
        client = gspread.authorize(creds)
        sheet = client.open_by_key("11eUWnFjsHTpHX81Ap6idXd-SDhzO1pCOQ0NNOptYxv8").sheet1
        sheet.append_rows([["ID", "Tiêu đề", "Ngày đăng", "Nội dung", "Nội dung edit", "Trạng thái", "Link"]])
        sheet.append_rows(data)
    except gspread.exceptions.APIError as e:
        print("Google Sheets API Error:", e.response.status_code)
    except Exception as e:
        print(f"Error writing to Google Sheets: {str(e)}")

# Hàm lấy bài viết và ghi vào Google Sheets
def get_articles_and_save_to_sheets(num_articles):
    try:
        # Thực hiện lấy bài viết (thay thế bằng cách lấy dữ liệu từ nguồn khác)
        articles = [
            ("Title 1", "http://example.com/1"),
            ("Title 2", "http://example.com/2")
        ]
        
        # Chỉ định các thông tin bài viết (giả sử bài viết có ngày và nội dung cố định)
        news_list = []
        for i, (title, link) in enumerate(articles):
            print(f"Đang xử lý bài {i + 1}: {title}")
            date = "2025-04-17"  # Giả sử ngày đăng
            content = "Nội dung bài viết giả lập."
            
            news_list.append([i + 1, title, date, content, "", "Chờ duyệt", link])
            time.sleep(0.3)

        print("Đang ghi dữ liệu vào Google Sheets...")
        write_to_google_sheets(news_list)
        return True
    except Exception as e:
        print(f"Lỗi khi lấy bài viết: {e}")
        return False

# Đoạn code Flask giữ nguyên để tiếp tục chạy app
@app.route('/')
def index():
    return render_template("index.html")

@app.route('/stream_logs', methods=["POST"])
def stream_logs():
    def generate_logs():
        try:
            num_articles = int(request.form.get("num_articles", 0))
            if num_articles <= 0:
                yield "data: ❌ Số lượng bài viết không hợp lệ.\n\n"
                yield "event: done\ndata: failed\n\n"
                return

            start_time = time.time()
            yield f"data: 📥 Yêu cầu lấy {num_articles} bài viết\n\n"
            yield "data: 🔄 Đang lấy danh sách bài viết...\n\n"

            if get_articles_and_save_to_sheets(num_articles):
                duration = round(time.time() - start_time, 2)
                yield f"data: ✅ Hoàn tất! ⏱️ Mất {duration} giây.\n\n"
                yield "event: done\ndata: success\n\"
            else:
                yield "data: ❌ Lỗi khi xử lý bài viết.\n\n"
                yield "event: done\ndata: failed\n\n"

        except Exception as e:
            yield f"data: ❌ Lỗi: {str(e)}\n\n"
            yield "event: done\ndata: failed\n\n"

    return Response(stream_with_context(generate_logs()), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(debug=False, threaded=True)
