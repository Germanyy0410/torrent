import requests # type: ignore
import os
from dotenv import load_dotenv # type: ignore
from datetime import datetime
import socket
# import peer_to_peer
import threading
import json
import netifaces # type: ignore

load_dotenv()
os.environ['PEER_PATH'] = '/home/germanyy0410/cn/torrent/input/'

def get_time():
    current_time = datetime.now()
    formatted_time = current_time.strftime("%d/%m/%y")
    return formatted_time

#* ================================ PIECES =================================
class InputPiece:
    def __init__(self, piece_number, size, status):
        self.piece_number = piece_number
        self.size = size
        self.status = status
    def to_dict(self):
        return {
            "piece_number": self.piece_number,
            "size": self.size,
            "status": self.status
        }

class Input:
    def __init__(self, input_name):
        self.input_name = input_name
        self.pieces = []
        self.input_size = 0
    def to_dict(self):
        return {
            "input_name": self.input_name,
            "pieces": [piece.to_dict() for piece in self.pieces]
        }
    def get_total_input_size(self):
        total_size = 0
        for piece in self.pieces:
            total_size += int(piece.size)
        self.input_size = total_size

class InputData:
    def __init__(self):
        self.inputs = []
    def to_dict(self):
        return {
            "inputs": [input_obj.to_dict() for input_obj in self.inputs]
        }

def get_pieces_status(Input ,folder_path):
    file_name = folder_path.split('/')[-1]

    for i in range(1, 5):
        file_part = str(i)  + '_' + file_name + '.part'
        file_path = os.path.join(folder_path, file_part)
        Input.pieces.append(InputPiece(i, os.path.exists(file_path)))


def get_all_input_pieces_status(InputData, folder_path):
    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        subfolders = [f.name for f in os.scandir(folder_path) if f.is_dir()]

        for folder in subfolders:
            current_input_file = Input(folder)
            get_pieces_status(current_input_file, os.path.join(f'{folder_path}{folder}'))
            InputData.inputs.append(current_input_file)
#* =========================================================================


#* =============================== DOWNLOAD ================================
def download_part(peer_ip, peer_port, file_path, receive_path):
    try:
        # Create a TCP socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connect to the peer
        client_socket.connect((peer_ip, int(peer_port)))

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


def download_file(peer_ip, peer_port, server_folder, pieces, file_name):
    threads = []

    for part in pieces:
        if not part.status:  # Only download parts that don't exist locally
            # Create file path
            file_path = os.path.join(f'{server_folder}/{part.piece_number}_{file_name}.part')
            receive_path = os.path.join(f'D:/CN_Ass/input/{file_name}/{part.piece_number}_{file_name}.part')
            print(receive_path)
            # Create and start a new thread for each part
            thread = threading.Thread(target=download_part, args=(peer_ip, peer_port, file_path, receive_path))
            thread.start()
            threads.append(thread)
            part.status = True

    # Wait for all threads to finish
    for thread in threads:
        thread.join()

#* =========================================================================


#* ======================== CONNECT PEER TO TRACKER ========================
def get_peer_ip():
    interfaces = netifaces.interfaces()
    for interface in interfaces:
        addresses = netifaces.ifaddresses(interface)
        if netifaces.AF_INET in addresses:
            for addr_info in addresses[netifaces.AF_INET]:
                if 'addr' in addr_info:
                    ip = addr_info['addr']
                    if ip.startswith('192.168.227.'):
                        return ip


def get_input_dir():
    return os.path.dirname(os.path.realpath(__file__)) + '/input/'


def connect_to_tracker():
    input_data = InputData()
    get_all_input_pieces_status(input_data, get_input_dir())
    input_data_json = json.dumps(input_data.to_dict())

    torrent_info = {
        "info_hash": "dd8255ecdc7ca55fb0bbf81323d87062db1f6d1c",
        "path": get_input_dir(),
        "peer_id": "Ubuntu " + get_time(),
        "port": 1234,
        "ip": get_peer_ip(),
        "tracked_pieces": input_data_json,
        "event": "started"
    }
    response = requests.get("http://" + os.environ['CURRENT_IP'] + ":8080/announce", params=torrent_info)
    return response.json()


if __name__ == "__main__":
    tracker_response = connect_to_tracker()
    print("Tracker response:", tracker_response)
#* =========================================================================


#* ========================== LISTEN FROM CLIENT ===========================
if __name__ == "__main__":
    # Tạo socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = get_peer_ip()
    port = 1234

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
                try:
                    client_socket.sendall(data)
                    print("File '{}' đã được gửi thành công.".format(file_path))
                except BrokenPipeError:
                    pass
        else:
            print("File '{}' không tồn tại.".format(file_path))

        # Đóng kết nối với máy khách
        client_socket.close()
#* =========================================================================



#* ============================== MERGE FILES ==============================
def merge_files(input_dir, output_file):
    parts = [part for part in os.listdir(input_dir) if part.endswith('.part')]  # Only select part files
    parts.sort(key=lambda x: int(x.split('_')[0])) # Sort the parts numerically

    with open(output_file, 'wb') as f:
        for part in parts:
            part_path = os.path.join(input_dir, part)
            with open(part_path, 'rb') as p:
                data = p.read()
                f.write(data)

    print(f"The parts in directory '{input_dir}' have been merged into the file '{output_file}'.")
#* =========================================================================

















    # pieces = get_pieces_status(input_folder_path)
    # download_file(peer_ip, peer_port, server_folder, pieces, user_file)

    # peer_ip = '192.168.227.130'
    # peer_port = 1234

    # user_file = input("Please input file name you want to download: ")
    # input_folder_path = (os.path.dirname(os.path.realpath(__file__)) + '/input/' + user_file).replace('\\', '/')
    # server_folder = os.environ['PEER_PATH'] + user_file

