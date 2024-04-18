import socket

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

    # Nhận dữ liệu từ máy khách
    received_data = client_socket.recv(1024).decode()
    print("Received data:", received_data)

    # Đóng kết nối
    client_socket.close()

# Đóng socket chính
server_socket.close()
