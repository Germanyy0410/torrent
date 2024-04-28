import requests # type: ignore
import os
from dotenv import load_dotenv # type: ignore
from datetime import datetime
import socket
import threading
import json
import hashlib
from tqdm import tqdm
import subprocess
import main
import pickle


load_dotenv()
os.environ['PEER_PATH'] = '/home/germanyy0410/cn/torrent/input/'

def get_time():
    current_time = datetime.now()
    formatted_time = current_time.strftime("%d/%m/%y")
    return formatted_time

#* ================================ PIECES =================================

class Piece:
    def __init__(self, piece_number, size, status, hash):
        self.piece_number = piece_number
        self.size = size
        self.status = status
        self.hash = hash
    def to_dict(self):
        return {
            "piece_number": self.piece_number,
            "size": self.size,
            "status": self.status,
            "hash": self.hash
        }

class File:
    def __init__(self, file_name, file_size, num_pieces, status):
        self.file_name = file_name
        self.file_size = file_size
        self.pieces = []
        self.num_pieces = num_pieces
        self.info_hash = ""
        self.piece_hashes = []
        self.status = status
    def to_dict(self):
        return {
            "file_name": self.file_name,
            "file_size": self.file_size,
            "pieces": [piece.to_dict() for piece in self.pieces],
            "num_pieces": self.num_pieces,
            "info_hash": self.info_hash,
            "piece_hashes": self.piece_hashes,
            "status": self.status,
        }


class Input:
    def __init__(self, input_name):
        self.input_name = input_name
        self.size = 0
        self.files = []
        self.piece_hashes = []
    def to_dict(self):
        return {
            "input_name": self.input_name,
            "input_size": self.size,
            "files": [file.to_dict() for file in self.files],
            "piece_hashes": self.piece_hashes
        }


class InputData:
    def __init__(self):
        self.inputs = []
    def to_dict(self):
        return {
            "inputs": [input_obj.to_dict() for input_obj in self.inputs]
        }


def get_pieces_status(file ,folder_path):
    file_name = file.file_name.rsplit(".", 1)[0]

    # Get file[info_hash]
    # torrent_file_path = folder_path + '/' + file_name + '.torrent'
    # file.info_hash = main.read_torrent(torrent_file_path)["info_hash"]

    for i in range(1, file.num_pieces + 1):
        file_part = file_name  + '_' + str(i) + '.part'
        file_path = os.path.join(folder_path, file_part)

        file_size = 0
        hash = ""
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            hash = generate_piece_hash(file_path)

        file.pieces.append(Piece(i, file_size, os.path.exists(file_path), hash))


def get_all_input_pieces_status(InputData, folder_path):
    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        subfolders = [f.name for f in os.scandir(folder_path) if f.is_dir()]

        for folder in subfolders:
            input = Input(folder)
            torrent_info, piece_hashes = main.read_torrent(main.get_torrent_path(folder))
            input.piece_hashes = piece_hashes

            for file in torrent_info["files"]:
                if ".torrent" in file["name"]:
                    break

                file_path = main.get_input_path(folder) + "/" + file["name"]
                status = False
                if os.path.exists(file_path):
                    status = True
                file_info = File(file["name"], file["length"], file["num_pieces"], status)
                get_pieces_status(file_info, main.get_input_path(folder) + "/parts/")
                input.files.append(file_info)

            InputData.inputs.append(input)

#* =========================================================================


#* =============================== DOWNLOAD ================================

def generate_piece_hash(file_path):
    with open(file_path, 'rb') as f:
        byte_data = f.read()

    sha1 = hashlib.sha1()
    sha1.update(byte_data)
    return sha1.digest().hex()


def verify_piece(torrent_name, file_name, file_path):
    torrent_info, piece_hashes = main.read_torrent(main.get_torrent_path(torrent_name))

    if generate_piece_hash(file_path) in piece_hashes[file_name]:
        return True

    return False


def upload_piece(client_socket, torrent_name, file_name, sender_path, receiver_path):
    print("\nUploading to peer...\n")

    if verify_piece(torrent_name, file_name, sender_path) == False:
        print("Error: Piece has been modified, cannot upload to peer(s).")
    else:

        # Send request type
        req = "upload_request"
        client_socket.send(req.encode())

        # Send piece path
        data_to_send=  {
            "file_path": str(receiver_path)
        }
        json_data = json.dumps(data_to_send)
        client_socket.send(json_data.encode('utf-8'))

        # Send piece data
        if os.path.exists(sender_path):
            with open(sender_path, 'rb') as file:
                data = file.read()
                client_socket.sendall(data)
                print("File '{}' has been uploaded successfully...".format(sender_path))


def download_piece(client_socket, file_name, sender_path, receiver_path):
    req = "download_request"
    client_socket.send(req.encode())

    # Send file path & piece hashes
    data_to_send = {
        "file_name": file_name,
        "file_path": str(sender_path),
    }
    json_data = json.dumps(data_to_send)
    client_socket.send(json_data.encode('utf-8'))

    # Receive piece size
    piece_size = int(client_socket.recv(1024).decode())

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

    # TODO: Later
    # merge_files()


def download_file(peer, input: Input, torrent_name):
    threads = []
    peer_ip = peer["ip"]
    peer_port = peer["port"]
    sender_folder = peer["path"]

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((peer_ip, int(peer_port)))

    # Send torrent name to peer
    client_socket.send(str(torrent_name).encode())

    # Receive torrent status from peer
    # peer_json = client_socket.recv(1000000000).decode('utf-8')
    # peer_info = json.loads(peer_json)

    for file in input.files:
        for part in file.pieces:
            if not part.status:
                sender_path = os.path.join(f'{sender_folder}{torrent_name}/parts/{file}_{part.piece_number}.part')
                receiver_path = os.path.join(f'D:/CN_Ass/input/{torrent_name}/parts/{file}_{part.piece_number}.part')

                # thread = threading.Thread(target=download_piece, args=(peer_ip, peer_port, sender_path, receiver_path, piece_hashes[part.piece_number - 1]))
                # thread.start()
                # threads.append(thread)

                download_piece(client_socket, file, sender_path, receiver_path)
                part.status = True
            else:
                sender_path = os.path.join(f'D:/CN_Ass/input/{torrent_name}/parts/{file}_{part.piece_number}.part')
                receiver_path = os.path.join(f'{sender_folder}{torrent_name}/parts/{file}_{part.piece_number}.part')

                # thread = threading.Thread(target=upload_piece, args=(peer_ip, peer_port, sender_path, receiver_path, piece_hashes))
                # thread.start()
                # threads.append(thread)

                upload_piece(client_socket, torrent_name, file, sender_path, receiver_path)

    # for thread in threads:
    #     thread.join()
    client_socket.close()

#* =========================================================================


#* ======================== CONNECT PEER TO TRACKER ========================

def get_peer_ip():
    try:
        output = subprocess.check_output(['hostname', '-I']).decode().strip()
        ip_address = output.split()[0]
    except Exception as e:
        print("Error:", e)
        ip_address = None
    return ip_address


def get_input_dir():
    return os.path.dirname(os.path.realpath(__file__)) + '/input/'


def connect_to_tracker():
    input_data = InputData()
    # get_all_input_pieces_status(input_data, get_input_dir())
    # input_data_json = json.dumps(input_data.to_dict())

    torrent_info = {
        "path": get_input_dir().replace("\\", "/"),
        "peer_id": "Ubuntu " + get_time(),
        "port": 1234,
        "ip": get_peer_ip(),
        # "pieces": input_data_json,
        "event": "started"
    }
    response = requests.get("http://" + os.environ['CURRENT_IP'] + ":8080/announce", params=torrent_info)
    return response.json()

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

    connect_to_tracker()
    print("Send response to tracker.")

    client_socket, client_address = server_socket.accept()

    # Receive torrent name
    torrent_name = client_socket.recv(1024).decode()

    # Send torrent status to client
    input = main.get_torrent_status(torrent_name)
    # inputs = json.dumps(input.to_dict())
    # client_socket.sendall(inputs.encode('utf-8'))

    while True:
        client_request = client_socket.recv(1024).decode()
        # Download
        if client_request == 'download_request':
            print("This is a download request...")
            # Receive file path & piece hashes
            received_data = client_socket.recv(1024).decode('utf-8')
            parsed_data = json.loads(received_data)
            file_path = parsed_data["file_path"].replace('//', '/')
            file_name = parsed_data["file_name"]
            print("Received file path:", file_path)

            # Send piece size to client
            client_socket.send(str(os.path.getsize(file_path)).encode())

            # Kiểm tra sự tồn tại của file và piece hash
            if os.path.exists(file_path):
                if verify_piece(torrent_name, file_name, file_path) == True:
                    print("Verified: Piece matched.")

                    with open(file_path, 'rb') as file:
                        data = file.read()
                        try:
                            client_socket.sendall(data)
                            print("File '{}' has sent successfully.".format(file_path))
                        except BrokenPipeError:
                            pass
                else:
                    print("Error: Piece has been modified.")

            else:
                client_socket.sendall("")
                print("File '{}' không tồn tại.".format(file_path))

        # Upload
        elif client_request == 'upload_request':
            print("This is a upload request...")
            received_data = client_socket.recv(1024).decode('utf-8')
            parsed_data = json.loads(received_data)

            # TODO: Receive piece_size
            file_path = parsed_data["file_path"]

            with open(file_path, 'wb') as file:
                progress_bar = tqdm(total=512 * 1024, unit='B', unit_scale=True)
                while True:
                    data = client_socket.recv(1024)
                    if not data:
                        break
                    file.write(data)
                    progress_bar.update(len(data))
                progress_bar.close()

            print(f"{file_path} is uploaded successfully...\n")

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

