import requests # type: ignore
import os
from dotenv import load_dotenv # type: ignore
from datetime import datetime
import socket
import threading
import json
import hashlib
import main
from tqdm import tqdm

if __name__ == "__main__":
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
        self.piece_hash = 0
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
        self.piece_hashes = []
        self.info_hash = ''
    def to_dict(self):
        return {
            "input_name": self.input_name,
            "pieces": [piece.to_dict() for piece in self.pieces],
            "input_size": self.input_size,
            "piece_hashes": [piece_hash.to_dict() for piece_hash in self.piece_hashes],
            "info_hash": self.info_hash

        }


class InputData:
    def __init__(self):
        self.inputs = []
    def to_dict(self):
        return {
            "inputs": [input_obj.to_dict() for input_obj in self.inputs]
        }


def get_pieces_status(Input ,folder_path):
    file_name = folder_path.split('/')[-1]

    # Get input[info_hash]
    torrent_file_path = folder_path + '/' + file_name + '.torrent'
    Input.info_hash = main.read_torrent(torrent_file_path)["info_hash"]

    # Get piece status
    parts = [part for part in os.listdir(folder_path) if part.endswith('.part')]  # Only select part files
    for i in range(1, len(parts) + 1):
        file_part = str(i)  + '_' + file_name + '.part'
        file_path = os.path.join(folder_path, file_part)

        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
        else:
            file_size = 0
        Input.pieces.append(InputPiece(i, file_size, os.path.exists(file_path)))


def get_all_input_pieces_status(InputData, folder_path):
    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        subfolders = [f.name for f in os.scandir(folder_path) if f.is_dir()]

        for folder in subfolders:
            current_input_file = Input(folder)
            get_pieces_status(current_input_file, os.path.join(f'{folder_path}{folder}'))
            InputData.inputs.append(current_input_file)

#* =========================================================================


#* =============================== DOWNLOAD ================================

def calculate_piece_hash_from_part(file_path):
    with open(file_path, 'rb') as f:
        byte_data = f.read()

    sha1 = hashlib.sha1()
    sha1.update(byte_data)
    return sha1.digest().hex()


def download_part(peer_ip, peer_port, sender_path, receiver_path, piece_hash):
    try:
        # Create a TCP socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connect to the peer
        client_socket.connect((peer_ip, int(peer_port)))

        data_to_send = {
            "file_path": str(sender_path),
            "piece_hash": piece_hash.hex()
        }
        json_data = json.dumps(data_to_send)

        # Send request for the file part
        client_socket.send(json_data.encode('utf-8'))

        # Receive piece size
        piece_size = 512 * 1024

        # Receive file data
        with open(receiver_path, 'wb') as file:
            progress_bar = tqdm(total=piece_size, unit='B', unit_scale=True)
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break
                file.write(data)
                progress_bar.update(len(data))
            progress_bar.close()

        print(f"{receiver_path} downloaded successfully.\n")

    except Exception as e:
        print("Error:", e)

    finally:
        client_socket.close()


def download_file(peer_ip, peer_port, sender_folder, pieces, piece_hashes, file_name):
    threads = []
    count = 1
    for part in pieces:
        if not part.status:  # Only download parts that don't exist locally
            # Create file path
            sender_file_path = os.path.join(f'{sender_folder}{file_name}/{part.piece_number}_{file_name}.part')
            receiver_path = os.path.join(f'D:/CN_Ass/input/{file_name}/{part.piece_number}_{file_name}.part')

            # Create and start a new thread for each part
            thread = threading.Thread(target=download_part, args=(peer_ip, peer_port, sender_file_path, receiver_path, piece_hashes[part.piece_number - 1]))
            part.status = True
            thread.start()
            threads.append(thread)
            # part.size = os.path.getsize(receiver_path)

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
        "path": get_input_dir(),
        "peer_id": "Ubuntu " + get_time(),
        "port": 1234,
        "ip": get_peer_ip(),
        "pieces": input_data_json,
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
        received_data = client_socket.recv(1024).decode('utf-8')
        parsed_data = json.loads(received_data)

        file_path = parsed_data["file_path"].replace('//', '/')
        piece_hash = parsed_data["piece_hash"]

        print("Received file path:", file_path)

        # client_socket.send(str(os.path.getsize(file_path)).encode('utf-8'))

        # Kiểm tra sự tồn tại của file và piece hash
        if os.path.exists(file_path):
            if calculate_piece_hash_from_part(file_path) == piece_hash:
                print("Piece hash mapped.")

                # Mở file và gửi dữ liệu cho máy khách
                with open(file_path, 'rb') as file:
                    data = file.read()
                    try:
                        client_socket.sendall(data)
                        print("File '{}' đã được gửi thành công.".format(file_path))
                    except BrokenPipeError:
                        pass
            else:
                print("Piece hash not found.")

        else:
            client_socket.sendall("")
            print("File '{}' không tồn tại.".format(file_path))

        # Đóng kết nối với máy khách
        client_socket.close()

#* =========================================================================


#* ============================== MERGE FILES ==============================

def merge_files(input_dir, output_file):
    parts = [part for part in os.listdir(input_dir) if part.endswith('.part')]  # Chọn chỉ các file parts
    parts.sort(key=lambda x: int(x.split('_')[0]))  # Sắp xếp các parts theo số thứ tự

    merged = False
    previous_number = None
    with open(output_file, 'wb') as f:
        for part in parts:
            number = int(part.split('_')[0])
            if previous_number is None or number == previous_number + 1:
                part_path = os.path.join(input_dir, part)
                with open(part_path, 'rb') as p:
                    data = p.read()
                    f.write(data)
                merged = True
                previous_number = number
            else:
                merged = False
                break

    if merged:
        print(f"The parts in directory '{input_dir}' have been merged into the file '{output_file}'.")
    else:
        os.remove(output_file)
        print("Cannot merge the parts due to discontinuous numbering.")

#* =========================================================================

















    # pieces = get_pieces_status(input_folder_path)
    # download_file(peer_ip, peer_port, server_folder, pieces, user_file)

    # peer_ip = '192.168.227.130'
    # peer_port = 1234

    # user_file = input("Please input file name you want to download: ")
    # input_folder_path = (os.path.dirname(os.path.realpath(__file__)) + '/input/' + user_file).replace('\\', '/')
    # server_folder = os.environ['PEER_PATH'] + user_file

