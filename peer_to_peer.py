import socket
import os
import threading
from dotenv import load_dotenv # type: ignore

load_dotenv()
os.environ['PEER_PATH'] = '/home/germanyy0410/cn/torrent/input/'

class FilePart:
    def __init__(self, file_number, existed):
        self.file_number = file_number
        self.existed = existed


def get_file_part_status(folder_path):
    file_name = folder_path.split('\\')[-1]
    file_parts = []

    for i in range(1, 5):
        file_part = str(i)  + '_' + file_name + '.part'
        file_path = os.path.join(folder_path, file_part)
        file_parts.append(FilePart(i, os.path.exists(file_path)))
    return file_parts


def download_part(peer_ip, peer_port, file_path, receive_path):
    try:
        # Create a TCP socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connect to the peer
        client_socket.connect((peer_ip, peer_port))

        # Send request for the file part
        client_socket.send(str(file_path).encode('utf-8'))

        # Receive file data
        with open(receive_path, 'wb') as file:
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break
                file.write(data)

        print(f"{receive_path} downloaded successfully.")

    except Exception as e:
        print("Error:", e)

    finally:
        # Close the socket
        client_socket.close()


def download_file(peer_ip, peer_port, server_folder, file_parts, file_name):
    threads = []

    for part in file_parts:
        if not part.existed:  # Only download parts that don't exist locally
            # Create file path
            file_path = os.path.join(f'{server_folder}/{part.file_number}_{file_name}.part')
            receive_path = os.path.join(f'D:/CN_Ass/input/{file_name}/{part.file_number}_{file_name}.part')
            print(receive_path)
            # Create and start a new thread for each part
            thread = threading.Thread(target=download_part, args=(peer_ip, peer_port, file_path, receive_path))
            thread.start()
            threads.append(thread)

    # Wait for all threads to finish
    for thread in threads:
        thread.join()

peer_ip = '192.168.227.130'
peer_port = 1234

user_file = input("Please input file name you want to download: ")
input_folder_path = os.path.dirname(os.path.realpath(__file__)) + '\input\\' + user_file
server_folder = os.environ['PEER_PATH'] + user_file

file_parts = get_file_part_status(input_folder_path)
# for file in file_parts:
#     print(f'{file.file_number}   {file.existed}')
download_file(peer_ip, peer_port, server_folder, file_parts, user_file)
