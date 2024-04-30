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
from prettytable import PrettyTable


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

    for file in piece_hashes:
        if file_name in file:
            if generate_piece_hash(file_path) in piece_hashes[file]:
                return True

    return False

def get_piece_size(piece_size):
    if piece_size >= 1024:
        kb_value = piece_size / 1024
        if kb_value >= 1024:
            mb_value = kb_value / 1024
            return str(round(mb_value, 2)) + "MB"
        else:
            return str(round(kb_value, 2)) + "KB"
    else:
        return str(round(piece_size, 2)) + "Bytes"

    return piece_size


def upload_piece(peer, torrent_name, file_name, sender_path, receiver_path):
    peer_ip = peer["ip"]
    peer_port = peer["port"]
    piece_name = sender_path.split("/")[-1]
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((peer_ip, int(peer_port)))

    # Send request type
    req = "upload_request"
    request = {
        "torrent_name": str(torrent_name),
        "request": str(req),
        "receiver_path": str(receiver_path),
        "file_name": str(file_name),
        "file_path": str(sender_path),
    }
    request_json = json.dumps(request)
    client_socket.send(request_json.encode('utf-8'))

    if verify_piece(torrent_name, file_name, sender_path) == False:
        print(f"Error: Piece {piece_name} has been modified, cannot upload to peer(s).")
    else:
        response = client_socket.recv(1024).decode('utf-8')
        if response == "False":
            print(f"Uploading: Connect successfully to [{peer_ip}, {peer_port}].")
            # Send piece data
            if os.path.exists(sender_path):
                with open(sender_path, 'rb') as file:
                    data = file.read()
                    client_socket.sendall(data)
                    print("File '{}' has been uploaded successfully...".format(sender_path.split("/")[-1]))

    client_socket.close()
    lock.release()


def get_existing_piece_num(folder_path, file_name):
    count = 0
    for piece in os.listdir(folder_path):
        if file_name in piece:
            count += 1
    return count


def print_download_progress(table, data, piece_size, file_name, piece_name, receiver_path, total_pieces):
    os.system('cls')

    progress_str = f"{len(data)}/{piece_size}"
    current_pieces = get_existing_piece_num(receiver_path.rsplit("/", 1)[0], file_name.rsplit(".", 1)[0])
    new_str = str(current_pieces) + " / " + str(total_pieces)
    table.clear_rows()
    table.add_row([file_name, piece_name, progress_str, new_str])
    print(table.get_string() + '\n')


def download_piece(peer, part, torrent_name, file_name, sender_path, receiver_path, total_pieces):
    peer_ip = peer["ip"]
    peer_port = peer["port"]
    piece_name = receiver_path.split("/")[-1]

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((peer_ip, int(peer_port)))

    req = "download_request"
    request = {
        "torrent_name": str(torrent_name),
        "request": str(req),
        "receiver_path": str(receiver_path),
        "file_name": str(file_name),
        "file_path": str(sender_path),
    }
    request_json = json.dumps(request)
    client_socket.send(request_json.encode('utf-8'))

    # Receive piece size
    piece_size = client_socket.recv(1024).decode()
    current_pieces = get_existing_piece_num(receiver_path.rsplit("/", 1)[0], file_name.rsplit(".", 1)[0])
    os.system("cls")
    if piece_size != "":
        print("\n===========================================================")
        print(f"Downloading: Connected to [{peer_ip}, {peer_port}].")

        progress_percent = int(current_pieces / int(total_pieces) * 100)
        max_progress_length = 60
        num_equals = min(int(progress_percent * max_progress_length / 100), max_progress_length)
        progress_bar_str = "|" + "=" * num_equals + "-" * (max_progress_length - num_equals) + "|"

        print(f"\nFile: {file_name} ({current_pieces}/{total_pieces})\t\t{progress_bar_str}")
        print(f"Piece: {piece_name} ({get_piece_size(int(piece_size))})\n")

        # Receive file data
        with open(receiver_path, 'wb') as file:
            progress_bar = tqdm(total=int(piece_size), unit='B', unit_scale=True)
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break
                file.write(data)
                progress_bar.update(len(data))
                # print_download_progress(table, tmp, piece_size, file_name, piece_name, receiver_path, total_pieces)
            progress_bar.close()

        part.status = True

        merge_files(file_name.rsplit(".", 1)[0], receiver_path.rsplit("/", 1)[0], get_output_path(torrent_name, file_name))
        # print(f"\n{piece_name} downloaded successfully.\n")
        print("===========================================================")
    else:
        print("File {} does not existed in peer.".format(piece_name))

    client_socket.close()
    lock.release()


lock = threading.Lock()

def download_file(peer, input: Input, torrent_name, threads):
    # threads = []
    sender_folder = peer["path"]

    for file in input.files:
        file_name = file.file_name.rsplit(".", 1)[0]
        for part in file.pieces:
            total_pieces = len(file.pieces)
            if not part.status:
                sender_path = os.path.join(f'{sender_folder}{torrent_name}/parts/{file_name}_{part.piece_number}.part')
                receiver_path = os.path.join(f'D:/CN_Ass/input/{torrent_name}/parts/{file_name}_{part.piece_number}.part')

                lock.acquire()

                thread = threading.Thread(target=download_piece, args=(peer, part, torrent_name, file.file_name, sender_path, receiver_path, total_pieces))
                thread.start()
                threads.append(thread)

                # download_piece(peer, torrent_name, file.file_name, sender_path, receiver_path, total_pieces)
                # merge_files(file_name, receiver_path.rsplit("/", 1)[0], get_output_path(torrent_name, file.file_name))
            else:
                sender_path = os.path.join(f'D:/CN_Ass/input/{torrent_name}/parts/{file_name}_{part.piece_number}.part')
                receiver_path = os.path.join(f'{sender_folder}{torrent_name}/parts/{file_name}_{part.piece_number}.part')

                lock.acquire()

                thread = threading.Thread(target=upload_piece, args=(peer, torrent_name, file_name, sender_path, receiver_path))
                thread.start()
                threads.append(thread)

                # upload_piece(peer, torrent_name, file_name, sender_path, receiver_path)

    # for thread in threads:
    #     thread.join()

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


def get_output_path(torrent_name, file):
    return os.path.dirname(os.path.realpath(__file__)).replace('\\', '/') + '/output/' + torrent_name + '/' + str(file)


def connect_to_tracker():
    torrent_info = {
        "path": get_input_dir().replace("\\", "/"),
        "peer_id": "Ubuntu " + get_time(),
        "port": 1234,
        "ip": get_peer_ip(),
        "event": "started"
    }
    response = requests.get("http://" + os.environ['CURRENT_IP'] + ":8080/announce", params=torrent_info)
    return response.json()

#* =========================================================================


#* ========================== LISTEN FROM CLIENT ===========================

def listen_from_client():
    # Tạo socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = get_peer_ip()
    port = 1234

    connect_to_tracker()
    print("Send response to tracker.")

    # Liên kết socket với địa chỉ IP và số cổng
    server_socket.bind((host, port))

    # Lắng nghe kết nối đến từ máy khách
    server_socket.listen(1)

    while True:
        print("Start listening...")
        client_socket, client_address = server_socket.accept()
        recv_input_json = client_socket.recv(1024).decode('utf-8')
        print(recv_input_json)
        recv_input = json.loads(recv_input_json)
        print("Recieved: torrent name & request.", recv_input)

        torrent_name = recv_input["torrent_name"]
        input = main.get_torrent_status(torrent_name)

        client_request = recv_input["request"]
        # Download
        if client_request == 'download_request':
            print("This is a download request...")

            # Receive file path & piece hashes
            file_path = recv_input["file_path"].replace('//', '/')
            file_name = recv_input["file_name"]
            print("Received: file.", recv_input)


            # Kiểm tra sự tồn tại của file và piece hash
            if os.path.exists(file_path):
                # Send piece size to client
                client_socket.send(str(os.path.getsize(file_path)).encode())

                if verify_piece(torrent_name, file_name, file_path) == True:
                    print("Verified: Piece matched.")

                    with open(file_path, 'rb') as file:
                        data = file.read()
                        try:
                            client_socket.sendall(data)
                            print("File '{}' has sent successfully.".format(file_path.split("/")[-1]))
                        except BrokenPipeError:
                            pass
                else:
                    print("Error: Piece has been modified.")

            else:
                piece_size = "0"
                client_socket.send(piece_size.encode('utf-8'))
                print("File '{}' does not existed.".format(file_path.split("/")[-1]))

        # Upload
        elif client_request == 'upload_request':
            print("This is a upload request...")
            file_path = recv_input["receiver_path"]

            isPieceExisted = False
            if os.path.exists(file_path):
                isPieceExisted = True

            message = "True" if isPieceExisted else "False"
            client_socket.send(message.encode('utf-8'))

            if message == "False":
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

def merge_files(file_name, input_dir, output_file):
    parts = [part for part in os.listdir(input_dir) if part.endswith('.part') and file_name in part]
    parts.sort(key=lambda x: int(x.split('_')[1].split(".")[0]))

    merged = False
    previous_number = None
    with open(output_file, 'wb') as f:
        for part in parts:
            number = int(part.split('_')[1].split(".")[0])
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

#* =========================================================================

if __name__ == "__main__":
    connect_to_tracker()
    print("Send response to tracker.")

    listen_from_client()
