import socket
import os

class FilePart:
    def __init__(self, file_number, existed):
        self.file_number = file_number
        self.existed = existed

def get_file_part_status(folder_path):
    file_parts = []
    for i in range(1, 5):
        file_name = str(i) + '.part'
        file_path = os.path.join(folder_path, file_name)
        file_parts.append(FilePart(i, os.path.exists(file_path)))
    return file_parts

file_parts = get_file_part_status('D:/CN_Ass/input/book')
for part in file_parts:
    print(f"{part.file_number} :: {part.existed}")

# def download_file(peer_ip, peer_port, server_filename, client_filename):
#     # Create a TCP socket
#     client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#     try:
#         # Connect to the peer
#         client_socket.connect((peer_ip, peer_port))

#         # Send request for the file
#         client_socket.send(server_filename.encode())

#         # Receive file data
#         with open(client_filename, 'wb') as file:
#             while True:
#                 data = client_socket.recv(1024)
#                 if not data:
#                     break
#                 file.write(data)

#         print("File downloaded successfully.")

#     except Exception as e:
#         print("Error:", e)

#     finally:
#         # Close the socket
#         client_socket.close()

# # Usage example
# peer_ip = '192.168.227.130'
# peer_port = 1234
# server_filename = '/home/germanyy0410/Desktop/text.txt'
# client_filename = 'text.txt'



# download_file(peer_ip, peer_port, server_filename, client_filename)

