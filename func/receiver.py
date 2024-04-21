import socket
from tqdm import tqdm

# host = '192.168.227.130'
host = '192.168.1.8'
port = 1234

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client_socket.connect((host, port))

# receive_path = 'D:/CN_Ass/func/res.mp4'
receive_path = '/home/germanyy0410/cn/torrent/func/output.mp4'
file_size = int(client_socket.recv(1024).decode())  # Receive file size

try:
    with open(receive_path, 'wb') as file:
        progress_bar = tqdm(total=file_size, unit='B', unit_scale=True)
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            file.write(data)
            progress_bar.update(len(data))
        progress_bar.close()
        print("\nReceive successfully")

except Exception as e:
    print("\nError: ", e)

finally:
    client_socket.close()
