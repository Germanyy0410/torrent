import json
from peer import *
import os
from bcoding import bdecode, bencode
import hashlib
import peer
import pickle
from tracker import *
import requests
from prettytable import PrettyTable

class colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'

def get_input_path(file_name):
    return (os.path.dirname(os.path.realpath(__file__)) + '/input/' + file_name).replace('\\', '/')


def get_output_path(file_name):
    return (os.path.dirname(os.path.realpath(__file__)) + '/output/' + file_name).replace('\\', '/')


def get_torrent_path(file_name):
    return get_input_path(file_name) + '/' + file_name + '.torrent'


#* ================================ TORRENT ===============================

def create_torrent(directory_path, tracker_url, piece_length=512 * 1024):
    # Khởi tạo danh sách các file
    files = []

    # Lặp qua tất cả các file trong thư mục
    for root, _, filenames in os.walk(directory_path):
        for filename in filenames:
            # Đường dẫn tuyệt đối của file
            file_path = os.path.join(root, filename)

            # Đọc nội dung của file
            with open(file_path, 'rb') as f:
                file_data = f.read()

            # Tính toán độ dài của file
            file_size = len(file_data)

            # Tính toán số lượng phần
            num_pieces = -(-file_size // piece_length)

            # Tính toán hash và kích thước của từng phần và sắp xếp chúng thành một danh sách
            pieces = []
            for i in range(0, file_size, piece_length):
                piece_data = file_data[i:i+piece_length]
                piece_hash = hashlib.sha1(piece_data).digest()
                piece_size = len(piece_data)
                pieces.append({'hash': piece_hash, 'length': piece_size})

            file_hash = hashlib.sha1(file_data).digest()

            # Thêm thông tin của file vào danh sách
            file_info = {
                'path': file_path.replace("\\", "/"),
                'name': file_path.replace("\\", "/").split('/')[-1],
                'length': file_size,
                'pieces': pieces,
                'num_pieces': num_pieces,
                'file_hash': file_hash
            }
            files.append(file_info)

    # Tạo thông tin của torrent
    torrent_info = {
        'info': {
            'name': directory_path,
            'piece length': piece_length,
            'files': files
        },
        'announce': tracker_url
    }

    info_hash = hashlib.sha1(bencode(torrent_info['info'])).digest()
    torrent_info['info']['info_hash'] = info_hash
    # Mã hóa thông tin của torrent bằng Bencoding
    torrent_data = bencode(torrent_info)

    # Lưu dữ liệu của torrent vào file
    torrent_file_path = os.path.join(directory_path, directory_path.split('/')[-1] + '.torrent')
    with open(torrent_file_path, 'wb') as torrent_file:
        torrent_file.write(torrent_data)

    print("\n{} is successfully created.\n".format(directory_path))


def read_torrent(torrent_file_path):
    with open(torrent_file_path, 'rb') as torrent_file:
        # Đọc dữ liệu từ file torrent
        torrent_data = torrent_file.read()

        # Giải mã dữ liệu bằng bencode
        decoded_data = bdecode(torrent_data)

        # Trích xuất thông tin cần thiết từ dữ liệu giải mã
        torrent_info = {
            'name': decoded_data['info']['name'],
            'piece_length': decoded_data['info']['piece length'],
            'announce': decoded_data['announce'],
            'info_hash': decoded_data['info']['info_hash'],
        }

        # Khởi tạo dict lưu trữ tên file và danh sách mã hash của các piece
        file_piece_hashes = {}

        # Kiểm tra xem torrent có nhiều file hay không
        if 'files' in decoded_data['info']:
            # Trường hợp torrent chứa nhiều file
            file_info_list = decoded_data['info']['files']
            files = []
            for file_info in file_info_list:
                file_path = '/'.join([torrent_info['name']] + file_info['path'].split('/'))
                file_length = file_info['length']
                file_hash = file_info['file_hash']
                file_num_pieces = file_info['num_pieces']
                file_pieces = file_info['pieces']
                file_name = file_info['name']
                files.append({'path': file_path, 'name': file_name, 'length': file_length, 'num_pieces': file_num_pieces, 'pieces': file_pieces, 'file_hash': file_hash})

                # Lưu trữ tên file và danh sách mã hash của các piece
                file_piece_hashes[file_name] = [piece['hash'].hex() for piece in file_pieces]

            torrent_info['files'] = files
        else:
            # Trường hợp torrent chỉ chứa một file
            file_path = torrent_info['name']
            file_name = file_path.split('/')[-1]
            file_length = decoded_data['info']['length']
            file_num_pieces = -(-file_length // torrent_info['piece_length'])
            file_pieces = [{'hash': decoded_data['info']['pieces'][i:i+20], 'length': torrent_info['piece_length']} for i in range(0, len(decoded_data['info']['pieces']), 20)]
            torrent_info['files'] = [{'path': file_path, 'name': file_name, 'length': file_length, 'num_pieces': file_num_pieces, 'pieces': file_pieces}]

            # Lưu trữ tên file và danh sách mã hash của các piece
            file_piece_hashes[file_name] = [piece['hash'].hex() for piece in file_pieces]

    # Trả về thông tin torrent và dict chứa tên file và danh sách mã hash của các piece
    return torrent_info, file_piece_hashes


def get_torrent_status(torrent_name):
    torrent_info, piece_hashes = read_torrent(get_torrent_path(torrent_name))
    input = Input(torrent_name)
    input.piece_hashes = piece_hashes

    for file in torrent_info["files"]:
        if ".torrent" in file:
            break

        file_path = get_output_path(torrent_name) + "/" + file["name"]
        status = False
        if os.path.exists(file_path):
            status = True
        file_info = File(file["name"], file["length"], file["num_pieces"], status)
        get_pieces_status(file_info, get_input_path(torrent_name) + "/parts/")
        input.files.append(file_info)

    return input


def get_peers_from_tracker():
    response = requests.get("http://" + os.environ['CURRENT_IP'] + ":8080/get_peers")
    return response.json()

#* ========================================================================

running = True


def torrent_start(torrent_name):
    peers = get_peers_from_tracker()
    print(peers)
    # torrent_name = input("Please input file name you want to download: ")
    input = get_torrent_status(torrent_name)
    inputs = json.dumps(input.to_dict())

    threads = []
    # Connect client to peer(s)
    for peer in peers.values():
        thread = threading.Thread(target=download_torrent, args=(peer, input, torrent_name, threads))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()


def torrent_show(torrent_name):
    torrent_info, piece_hashes = read_torrent(get_torrent_path(torrent_name))
    print("\nannounce URL: {}".format(torrent_info["announce"]))
    print("info hash: {}\n".format(torrent_info["info_hash"].hex()))

    table = PrettyTable(["file", "size", "piece count", "file hash"])
    for file in torrent_info["files"]:
        table.add_row([file["name"], get_piece_size(file["length"]), file["num_pieces"], file["file_hash"].hex()])
    print(table.get_string() + '\n')

# def user_input_thread():
#     global running
#     input()
#     running = False
#     user_command = input("Nhập câu lệnh: ")
#     if user_command == "b-create":
#         # TODO:
#         print("a")
#     elif user_command == "b-start":
#         # TODO:
#         print("a")
#     elif user_command == "b-show":
#         # TODO:
#         print("a")
#     elif user_command == "b-info":
#         # TODO:
#         print("a")

# input_thread = threading.Thread(target=user_input_thread)
# input_thread.start()


#* ========================== START APPLICATION ===========================
if __name__ == '__main__':
    # text_based = """
    #  ___  ___  _____   _____  ___   ___  ___  _  _  _____
    # | _ )|_ _||_   _| |_   _|/ _ \ | _ \| __|| \| ||_   _|
    # | _ \ | |   | |     | | | (_) ||   /| _| | .` |  | |
    # |___/|___|  |_|     |_|  \___/ |_|_\|___||_|\_|  |_|
    # """
    # print(text_based)

    # input(colors.GREEN + ">> Enter command hehe: " + colors.RESET)

    # print("\nList of torrent files:")
    # print("   |-- books.torrent")
    # print("   |-- videos.torrent")
    # print("   |-- slides.torrent")

    # input(colors.GREEN + "\n>> Enter command hehe: " + colors.RESET)


    # print("\nopening books.torrent...")

    # torrent_show('books')
    # create_torrent("D:/CN_Ass/output/books", 'http:/10.46.153.20:8080/announce')
     # Calculate elapsed time
    torrent_name = 'books'
    torrent_start(torrent_name)

#* ========================================================================
