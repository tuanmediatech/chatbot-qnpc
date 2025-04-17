import sys
import time

def lay_bai(so_bai):
    print(f"👉 Đang xử lý lấy {so_bai} bài viết...")
    # Giả lập thời gian lấy bài (bạn có thể thay bằng code thực)
    for i in range(so_bai):
        print(f"✅ Đã lấy bài {i+1}")
        time.sleep(2)  # mỗi bài 2s
    print("🎯 Hoàn thành việc lấy bài!")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        try:
            so_bai = int(sys.argv[1])
            lay_bai(so_bai)
        except ValueError:
            print("⚠️ Tham số truyền vào phải là số nguyên!")
    else:
        print("⚠️ Bạn chưa truyền số lượng bài viết cần lấy.")
