import socket
import os
import time

class FilePart:
    def __init__(self, file_number, existed):
        self.file_number = file_number
        self.existed = existed

def get_file_part_status(folder_path, file_name):
    file_parts = []

    for i in range(1, 5):
        file_part = str(i)  + '_' + file_name + '.part'
        file_path = os.path.join(folder_path, file_part)
        file_parts.append(FilePart(i, os.path.exists(file_path)))
    return file_parts

def download_file(peer_ip, peer_port, server_folder, file_parts):
    # Create a TCP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Connect to the peer
        client_socket.connect((peer_ip, peer_port))

        # Iterate through file parts
        for part in file_parts:
            if not part.existed:  # Only download parts that don't exist locally
                # Send request for the file part
                client_socket.send(str(part.file_number).encode())

                # Receive file data
                file_path = os.path.join('D:/CN_Ass/input/book/', f'{part.file_number}.part')
                with open(file_path, 'wb') as file:
                    while True:
                        data = client_socket.recv(1024)
                        if not data:
                            break
                        file.write(data)

                print(f"Part {part.file_number} downloaded successfully.")

    except Exception as e:
        print("Error:", e)

    finally:
        # Close the socket
        client_socket.close()

# Usage example
peer_ip = '192.168.227.130'
peer_port = 1234
server_folder = '/home/germanyy0410/Desktop/cn/torrent/input/excel'

file_parts = get_file_part_status('D:/CN_Ass/input/excel', 'excel')

download_file(peer_ip, peer_port, server_folder, file_parts)