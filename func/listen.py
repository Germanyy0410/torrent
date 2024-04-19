import socket
import os

# Tạo socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Xác định địa chỉ IP và số cổng
host = '192.168.227.130'  # Thay thế bằng địa chỉ IP của Ubuntu
port = 1234  # Số cổng

# Liên kết socket với địa chỉ IP và số cổng
server_socket.bind((host, port))

# Lắng nghe kết nối đến từ máy khách
server_socket.listen(1)

while True:
    # Chấp nhận kết nối từ máy khách
    client_socket, client_address = server_socket.accept()

    # Nhận đường dẫn của file từ máy khách
    file_path = client_socket.recv(1024).decode()
    print("Received file path:", file_path)

    # Kiểm tra sự tồn tại của file
    if os.path.exists(file_path):
        # Mở file và gửi dữ liệu cho máy khách
        with open(file_path, 'rb') as file:
            data = file.read()
            client_socket.sendall(data)
            print("File '{}' đã được gửi thành công.".format(file_path))
    else:
        print("File '{}' không tồn tại.".format(file_path))

    # Đóng kết nối với máy khách
    client_socket.close()

# Đóng socket chính
server_socket.close()
