# import threading

# # Biến để đánh dấu trạng thái của chương trình (đang chạy hoặc đã dừng)
# running = True

# # Hàm được thực thi khi nhận input từ người dùng
# def user_input_thread():
#     global running
#     running = False
#     while True:
#       user_command = input("Nhập câu lệnh: ")
#       if user_command == "cli":
#           # Gọi hàm khác khi người dùng nhập lệnh "start"
#           print("Bắt đầu thực thi hàm...")
#           # Thực thi hàm khác ở đây

# # Tạo và khởi chạy thread để lắng nghe input từ người dùng
# input_thread = threading.Thread(target=user_input_thread)
# input_thread.start()

# # # Vòng lặp chính của chương trình
# # while running:
# #     # Thực hiện các công việc chính của chương trình ở đây
# #     print("Chương trình đang chạy...")

# # a = """
# #   ___  ___  _____   _____  ___   ___  ___  _  _  _____
# #  | _ )|_ _||_   _| |_   _|/ _ \ | _ \| __|| \| ||_   _|
# #  | _ \ | |   | |     | | | (_) ||   /| _| | .` |  | |
# #  |___/|___|  |_|     |_|  \___/ |_|_\|___||_|\_|  |_|

# # """
# # print(a)
# # import atexit
# # import os

# # file_path = "test.txt"

# # def cleanup():
# #     if os.path.exists(file_path):
# #         os.remove(file_path)
# #         print("File đã được xoá.")

# # def main():
# #     # Đăng ký hàm cleanup để được gọi khi chương trình kết thúc
# #     atexit.register(cleanup)

# #     # Mã chương trình của bạn
# #     # Ví dụ: ghi dữ liệu vào file
# #     with open(file_path, "w") as file:
# #       while True:
# #         file.write("Hello, world!")

# # if __name__ == "__main__":
# #     main()

# import threading
# import time
# import random

# # Mutex lock để đảm bảo chỉ một thread truy cập vào một mảnh dữ liệu cùng một thời điểm
# mutex = threading.Lock()

# # Semaphore để giới hạn số lượng mảnh dữ liệu được tải xuống cùng một lúc
# max_concurrent_downloads = 3
# semaphore = threading.Semaphore(max_concurrent_downloads)

# # Danh sách các mảnh dữ liệu của tệp torrent
# pieces = [i for i in range(10)]

# # Hàm để tải mảnh dữ liệu từ tệp torrent
# def download_piece(piece_id):
#     print(f"Thread bắt đầu tải mảnh dữ liệu {piece_id}")

#     # Giả lập thời gian tải xuống
#     time.sleep(random.uniform(0.5, 2))

#     print(f"Thread đã tải xong mảnh dữ liệu {piece_id}")

# # Hàm để thực thi việc tải xuống các mảnh dữ liệu
# def download_torrent():
#     while pieces:
#         # Kiểm tra xem có mảnh dữ liệu nào khả dụng không
#         piece_id = None
#         with mutex:
#             if pieces:
#                 piece_id = pieces.pop(0)

#         if piece_id is not None:
#             # Kiểm tra xem có thể tải xuống mảnh dữ liệu mới không
#             if semaphore.acquire(blocking=False):
#                 thread = threading.Thread(target=download_piece, args=(piece_id,))
#                 thread.start()
#             else:
#                 print("Đã đạt tới giới hạn tải xuống, đợi một chút trước khi tiếp tục...")
#                 time.sleep(1)

# # Tạo và khởi chạy thread để tải xuống các mảnh dữ liệu
# download_thread = threading.Thread(target=download_torrent)
# download_thread.start()

# # Chờ thread tải xuống hoàn thành
# download_thread.join()

# print("Tải xuống hoàn tất")
str = ["as", "asv"]
print(str[0])