import socket

# host = '192.168.227.130'
host = '192.168.1.8'
port = 1234

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client_socket.connect((host, port))

receive_path = '/home/germanyy0410/cn/torrent/output'
# receive_path = 'D:/CN_Ass/func/res.mp4'

try:
  with open(receive_path, 'wb') as file:
    while True:
      data = client_socket.recv(1024)
      if not data:
        break
      file.write(data)

  print("Receive successfully")

except Exception as e:
  print("Error: ", e)

finally:
  client_socket.close()