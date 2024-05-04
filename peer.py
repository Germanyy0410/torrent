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
from prettytable import PrettyTable
import time
import concurrent.futures

max_workers = 2

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
            return str(round(mb_value, 2)) + " MB"
        else:
            return str(round(kb_value, 2)) + " KB"
    else:
        return str(round(piece_size, 2)) + " Bytes"

    return piece_size


def upload_piece(peer, torrent_name, full_file_name, file_name, sender_path, receiver_path):
    peer_ip = peer["ip"]
    peer_port = peer["port"]
    piece_name = sender_path.split("/")[-1]
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((peer_ip, int(peer_port)))

    elapsed_time = time.time() - start_time
    hours, remainder = divmod(elapsed_time, 3600)
    minutes, seconds = divmod(remainder, 60)
    elapsed_time_str = "{:02}:{:02}:{:02}".format(int(hours), int(minutes), int(seconds))

    # Send request type
    req = "upload_request"
    request = {
        "torrent_name": str(torrent_name),
        "request": str(req),
        "receiver_path": str(receiver_path),
        "file_name": str(full_file_name),
        "file_path": str(sender_path),
    }
    request_json = json.dumps(request)
    client_socket.send(request_json.encode('utf-8'))

    if verify_piece(torrent_name, file_name, sender_path) == False:
        print(f"Error: Piece {piece_name} has been modified, cannot upload to peer(s).")
    else:
        response = client_socket.recv(1024).decode('utf-8')
        if response == "False":
            print("\n\nelapsed time: " + main.colors.YELLOW + elapsed_time_str + main.colors.RESET)
            print("======================================================================================")
            print(main.colors.RED + "Uploading:" + main.colors.RESET + f" Connected to [{peer_ip}, {peer_port}].")

            print("Piece hash matched: {}".format(generate_piece_hash(sender_path)))
            # Send piece data
            if os.path.exists(sender_path):
                with open(sender_path, 'rb') as file:
                    data = file.read()
                    client_socket.sendall(data)
                    print("\nFile '{}' has been uploaded successfully...".format(sender_path.split("/")[-1]))
            print("======================================================================================")

    client_socket.close()
    # lock.release()


def get_existing_piece_num(folder_path, file_name):
    count = 0
    for piece in os.listdir(folder_path):
        if file_name in piece:
            count += 1
    return count


print_lock = threading.Lock()


def download_piece(peer, part, torrent_name, file_name, sender_path, receiver_path, total_pieces, table):
    peer_ip = peer["ip"]
    peer_port = peer["port"]
    piece_name = receiver_path.split("/")[-1]

    elapsed_time = time.time() - start_time
    hours, remainder = divmod(elapsed_time, 3600)
    minutes, seconds = divmod(remainder, 60)
    elapsed_time_str = "{:02}:{:02}:{:02}".format(int(hours), int(minutes), int(seconds))

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

    output = ""
    # Receive piece size
    piece_size = client_socket.recv(1024).decode()
    current_pieces = get_existing_piece_num(receiver_path.rsplit("/", 1)[0], file_name.rsplit(".", 1)[0])
    # os.system("cls")
    if piece_size != "":

        output += ("\n\n\nelapsed time: " + main.colors.YELLOW + elapsed_time_str + main.colors.RESET)
        output += ("\n--------------------------------------------------------------------------------------\n")
        output += (main.colors.RED + "Downloading:" + main.colors.RESET + f" Connected to [{peer_ip}, {peer_port}].")
        progress_percent = int(current_pieces / int(total_pieces) * 100)
        max_progress_length = 60
        num_equals = min(int(progress_percent * max_progress_length / 100), max_progress_length)
        progress_bar_str = "|" + "=" * num_equals + "-" * (max_progress_length - num_equals) + "|"
        output += (f"\n•  File: {file_name} ({current_pieces}/{total_pieces})\t\t{progress_bar_str}")
        output += (f"\n•  Piece: {piece_name} ({get_piece_size(int(piece_size))})\n")

        # Receive file data
        with open(receiver_path, 'wb') as file:
            # progress_bar = tqdm(total=int(piece_size), desc=f"{piece_name}", unit='B', unit_scale=True)
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break
                file.write(data)
                # progress_bar.update(len(data))

                # piece_percent = int(os.path.getsize(receiver_path) / int(piece_size) * 100)
                # max_length = 50
                # num_equal = min(int(piece_percent * max_length / 100), max_length)
                # progress_str = "|" + "=" * num_equal + "-" * (max_length - num_equal) + "|"

                # for row in table._rows:
                #     if file_name in row[0]:
                #         row[1] = f'{current_pieces}/{total_pieces}'
                #         row[2] = piece_name
                #         row[3] = peer_ip
                #         row[4] = peer_port
                #         row[5] = progress_str
                #         row[6] = ""

                # with print_lock:
                #     os.system("cls")
                #     print(table.get_string())

            # progress_bar.close()

        print(output + "\n--------------------------------------------------------------------------------------")
        part.status = True

        merge_files(file_name.rsplit(".", 1)[0], receiver_path.rsplit("/", 1)[0], get_output_path(torrent_name, file_name))

    else:
        print("File {} does not existed in peer.".format(piece_name))

    client_socket.close()
    # lock.release()


def get_files_progress(files, torrent_name, current_file):
    table = PrettyTable(["File", "Progress"])
    progress_bar = [tqdm(total=len(file.pieces), desc=f"Tiến trình {i.file_name}", unit="file", leave=False) for i in files]

    for i, file in enumerate(files):
        total_pieces = len(file.pieces)
        current_pieces = 0
        file_name = file.file_name.rsplit(".", 1)[0]
        path = os.getcwd() + "\\input\\" + torrent_name + "\parts"

        for part in os.listdir(path):
            if file_name in part:
                current_pieces += 1

        progress_bar[i].update(1)
    #     progress_percent = int(current_pieces / int(total_pieces) * 100)
    #     max_progress_length = 60
    #     num_equals = min(int(progress_percent * max_progress_length / 100), max_progress_length)
    #     progress_bar_str = "|" + "=" * num_equals + "-" * (max_progress_length - num_equals) + "|"
    #     if file.file_name == current_file:
    #         progress_bar_str = main.colors.GREEN + progress_bar_str + main.colors.RESET
    #     table.add_row([file.file_name, progress_bar_str])
    # print(table.get_string())


# lock = threading.Lock()
start_time = time.time()


def download_file(peer, file, torrent_name, table):
    sender_folder = peer["path"]

    file_name = file.file_name.rsplit(".", 1)[0]
    for part in file.pieces:
        total_pieces = len(file.pieces)

        if not part.status:
            sender_path = os.path.join(f'{sender_folder}{torrent_name}/parts/{file_name}_{part.piece_number}.part')
            receiver_path = os.path.join(f'D:/CN_Ass/input/{torrent_name}/parts/{file_name}_{part.piece_number}.part')

            # lock.acquire()

            download_piece(peer, part, torrent_name, file.file_name, sender_path, receiver_path, total_pieces, table)
            # get_files_progress(input.files, torrent_name, file.file_name)

        else:
            sender_path = os.path.join(f'D:/CN_Ass/input/{torrent_name}/parts/{file_name}_{part.piece_number}.part')
            receiver_path = os.path.join(f'{sender_folder}{torrent_name}/parts/{file_name}_{part.piece_number}.part')

            # lock.acquire()

            upload_piece(peer, torrent_name, file.file_name, file_name, sender_path, receiver_path)


def download_torrent(peers, input: Input, torrent_name):
    threads = []
    max_threads = len(peers)
    # semaphore = threading.Semaphore(max_threads)

    table = PrettyTable(["file", "no .piece", "current piece", "ip", "port", "progress", "download speed"])

    for file in input.files:
        table.add_row([file.file_name, "./.", "", "0.0.0.0", "3000", "0%", "0 MB/s"])

    peer_list = []
    for peer in peers.values():
        peer_list.append(peer)

    for file in input.files:
        if len(peer_list) == 0:
            for peer in peers.values():
                peer_list.append(peer)
        peer = peer_list[0]
        peer_list = peer_list[1:]

        # semaphore.acquire()
        thread =threading.Thread(target=download_file, args=(peer, file, torrent_name, table), name=file.file_name)
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()


    # try:
    #     with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
    #         futures = []

    #         for file in input.files:
    #             if len(peer_list) == 0:
    #                 for peer in peers.values():
    #                     peer_list.append(peer)
    #             peer = peer_list[0]
    #             peer_list = peer_list[1:]

    #             future = executor.submit(download_file, peer, file, torrent_name, table)
    #             futures.append(future)

    #         for future in concurrent.futures.as_completed(futures):
    #             # Xử lý kết quả nếu cần
    #             print('asda')
    #             pass  # Ở đây chúng ta không cần xử lý kết quả, chỉ đợi các thread hoàn thành

    # except RuntimeError as e:
    #     print("Lỗi: Không thể tạo ThreadPoolExecutor:", e)
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
        print("\n\nStart listening...")
        client_socket, client_address = server_socket.accept()
        recv_input_json = client_socket.recv(1024).decode('utf-8')
        # print(recv_input_json)
        recv_input = json.loads(recv_input_json)
        # print("Recieved: torrent name & request.", recv_input)

        torrent_name = recv_input["torrent_name"]
        input = main.get_torrent_status(torrent_name)

        client_request = recv_input["request"]
        # Download
        if client_request == 'download_request':
            print("This is a download request...")

            # Receive file path & piece hashes
            file_path = recv_input["file_path"].replace('//', '/')
            file_name = recv_input["file_name"]
            # print("Received: file.", recv_input)

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
            file_name = recv_input["file_name"]
            receiver_path = recv_input["receiver_path"].rsplit("/", 1)[0]
            torrent_name = recv_input["torrent_name"]

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
                merge_files(file_name.rsplit(".", 1)[0], receiver_path, get_output_path(torrent_name, file_name) + file_name.rsplit(".", 1)[1])



        # Đóng kết nối với máy khách
        client_socket.close()

#* =========================================================================


#* ============================== MERGE FILES ==============================

def merge_files(file_name, input_dir, output_file):
    parts = [part for part in os.listdir(input_dir) if part.endswith('.part') and file_name in part]
    parts.sort(key=lambda x: int(x.rsplit('_', 1)[1].split(".")[0]))

    previous_number = None
    with open(output_file, 'wb') as f:
        for part in parts:
            number = int(part.rsplit('_', 1)[1].split(".")[0])
            if previous_number is None or number == previous_number + 1:
                part_path = os.path.join(input_dir, part)
                with open(part_path, 'rb') as p:
                    data = p.read()
                    f.write(data)
                previous_number = number
            else:
                break

#* =========================================================================

if __name__ == "__main__":
    connect_to_tracker()
    print("Send response to tracker.")
    listen_from_client()
