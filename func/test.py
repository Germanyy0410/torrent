import threading

# Biến để đánh dấu trạng thái của chương trình (đang chạy hoặc đã dừng)
running = True

# Hàm được thực thi khi nhận input từ người dùng
def user_input_thread():
    global running
    running = False
    while True:
      user_command = input("Nhập câu lệnh: ")
      if user_command == "cli":
          # Gọi hàm khác khi người dùng nhập lệnh "start"
          print("Bắt đầu thực thi hàm...")
          # Thực thi hàm khác ở đây

# Tạo và khởi chạy thread để lắng nghe input từ người dùng
input_thread = threading.Thread(target=user_input_thread)
input_thread.start()

# # Vòng lặp chính của chương trình
# while running:
#     # Thực hiện các công việc chính của chương trình ở đây
#     print("Chương trình đang chạy...")

# a = """
#   ___  ___  _____   _____  ___   ___  ___  _  _  _____
#  | _ )|_ _||_   _| |_   _|/ _ \ | _ \| __|| \| ||_   _|
#  | _ \ | |   | |     | | | (_) ||   /| _| | .` |  | |
#  |___/|___|  |_|     |_|  \___/ |_|_\|___||_|\_|  |_|

# """
# print(a)
# import atexit
# import os

# file_path = "test.txt"

# def cleanup():
#     if os.path.exists(file_path):
#         os.remove(file_path)
#         print("File đã được xoá.")

# def main():
#     # Đăng ký hàm cleanup để được gọi khi chương trình kết thúc
#     atexit.register(cleanup)

#     # Mã chương trình của bạn
#     # Ví dụ: ghi dữ liệu vào file
#     with open(file_path, "w") as file:
#       while True:
#         file.write("Hello, world!")

# if __name__ == "__main__":
#     main()

import peer
