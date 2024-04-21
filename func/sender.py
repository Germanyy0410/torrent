import socket

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = '192.168.1.8'
port = 1234

server_socket.bind((host, port))

server_socket.listen(1)

while True:
  client_socket, client_address = server_socket.accept()

  file_path = 'D:/CN_Ass/func/Inside Part 1.mp4'

  with open(file_path, 'rb') as file:
    data = file.read()
    try:
      client_socket.sendall(data)
      print("Send successfully")
    except BrokenPipeError:
      pass

  client_socket.close()