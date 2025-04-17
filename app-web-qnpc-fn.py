from flask import Flask, render_template, request, Response, stream_with_context
from playwright.sync_api import sync_playwright
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time
import threading
import os
import sys
import webbrowser

# ✅ Đường dẫn tới browser của Playwright (nếu cần)
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = os.path.join(os.getcwd(), "pw-browsers")

# ✅ Cấu hình Google Sheets
json_keyfile = "my-project-74363-183-e47d0199afbb.json"
spreadsheet_id = "11eUWnFjsHTpHX81Ap6idXd-SDhzO1pCOQ0NNOptYxv8"

app = Flask(__name__, template_folder="templates", static_folder="static")

# ✅ Hàm mở trình duyệt (chỉ dùng cho Flask app)
def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000")

# ✅ Hàm lấy bài viết và ghi vào Google Sheets
def get_articles_and_save_to_sheets(num_articles):
    try:
        print(f"📥 Đang lấy {num_articles} bài viết...")
        articles = get_articles(num_articles)
        if not articles:
            print("❌ Không lấy được bài viết.")
            return False

        news_list = []
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            for i, (title, link) in enumerate(articles):
                print(f"🔎 Đang xử lý bài {i + 1}: {title}")
                page.goto(link)
                try:
                    date = page.locator("#mvcContainer-11766 .heading-content p span").nth(0).inner_text(timeout=60000)
                except:
                    date = "Không có ngày"

                content_locator = page.locator("#mvcContainer-11766 .article-content p").all()
                content = " ".join([p.inner_text() for p in content_locator]) if content_locator else "Không có nội dung"

                news_list.append([i + 1, title, date, content, "", "Chờ duyệt", link])
                time.sleep(0.3)

            browser.close()

        print("✅ Đang ghi dữ liệu vào Google Sheets...")
        write_to_google_sheets(news_list)
        return True
    except Exception as e:
        print(f"❌ Lỗi khi lấy bài viết: {e}")
        return False

# ✅ Hàm ghi vào Google Sheets
def write_to_google_sheets(data):
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name(json_keyfile, scope)
        client = gspread.authorize(creds)
        sheet = client.open_by_key(spreadsheet_id).sheet1
        sheet.clear()
        sheet.append_rows([["ID", "Tiêu đề", "Ngày đăng", "Nội dung", "Nội dung edit", "Trạng thái", "Link"]])
        sheet.append_rows(data)
    except gspread.exceptions.APIError as e:
        print("❌ Google Sheets API Error:", e.response.status_code)
    except Exception as e:
        print(f"❌ Error writing to Google Sheets: {str(e)}")

# ✅ Placeholder: Hàm này bạn cần tự định nghĩa
def get_articles(num_articles):
    with sync_playwright() as p:
        print("🔗 Đang kiểm tra khả năng truy cập trang web...")
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://pcquangngai.cpc.vn", timeout=60000)
        page.wait_for_selector("#mvcContainer-12285")

        articles_locator = page.locator("#mvcContainer-12285").locator("a.title-link")
        articles = articles_locator.all()
        article_list = [(articles[i].inner_text(), articles[i].get_attribute("href")) for i in range(min(num_articles, len(articles)))]

        browser.close()
        return article_list



# ✅ Route Flask (chạy trên trình duyệt)
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
                yield "event: done\ndata: success\n\n"
            else:
                yield "data: ❌ Lỗi khi xử lý bài viết.\n\n"
                yield "event: done\ndata: failed\n\n"

        except Exception as e:
            yield f"data: ❌ Lỗi: {str(e)}\n\n"
            yield "event: done\ndata: failed\n\n"

    return Response(stream_with_context(generate_logs()), mimetype='text/event-stream')

# ✅ Nếu chạy từ Terminal hoặc từ Bot Telegram
if __name__ == '__main__':
    # Nếu gọi từ terminal (có tham số)
    if len(sys.argv) > 1:
        try:
            num_articles = int(sys.argv[1])
            print(f"👉 Được gọi từ bot Telegram: lấy {num_articles} bài viết")
            get_articles_and_save_to_sheets(num_articles)
        except Exception as e:
            print(f"❌ Lỗi khi xử lý yêu cầu từ bot Telegram: {e}")
    else:
        # Mặc định chạy Flask nếu không có tham số
        threading.Timer(1.5, open_browser).start()
        app.run(debug=False, threaded=True)
