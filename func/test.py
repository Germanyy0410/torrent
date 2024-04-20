import socket

# Tạo socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Địa chỉ IP và số cổng của máy ảo Ubuntu
host = '192.168.227.130'  # Địa chỉ IP của máy ảo Ubuntu
port = 1234  # Số cổng mà server đang lắng nghe

# Kết nối đến máy chủ trên máy ảo Ubuntu
client_socket.connect((host, port))

# Nhập đường dẫn của file trên máy ảo Ubuntu
file_path = '/home/germanyy0410/logbuf.c'

# Gửi yêu cầu tải file
client_socket.send(file_path.encode())

# Nhận dữ liệu từ máy chủ (dữ liệu của file)
with open(file_path.split('/')[-1], 'wb') as file:
    while True:
        data = client_socket.recv(1024)
        if not data:
            print("File đã được tải về thành công.")
            break
        file.write(data)


# Đóng kết nối
client_socket.close()
