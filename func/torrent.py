from bcoding import bdecode, bencode
import hashlib
import json
import math
import bencodepy

def create_torrent(file_path, tracker_url, piece_length=512 * 1024):
    # Đọc nội dung của tập tin
    with open(file_path, 'rb') as f:
        file_data = f.read()

    # Tính toán độ dài của tập tin
    file_size = len(file_data)

    # Tính toán số lượng phần
    num_pieces = -(-file_size // piece_length)

    # Tính toán hash của từng phần và sắp xếp chúng thành một danh sách
    piece_hashes = [hashlib.sha1(file_data[i:i+piece_length]).digest() for i in range(0, file_size, piece_length)]

    # Tạo thông tin của torrent
    torrent_info = {
        'info': {
            'name': file_path,
            'piece length': piece_length,
            'length': file_size,
            'pieces': b''.join(piece_hashes)
        },
        'announce': tracker_url
    }

    # Mã hóa thông tin của torrent bằng Bencoding
    torrent_data = bencodepy.encode(torrent_info)

    # Lưu dữ liệu của torrent vào file
    with open(file_path + '.torrent', 'wb') as torrent_file:
        torrent_file.write(torrent_data)


def load_from_path(path):
    with open(path, 'rb') as file:
        contents = bdecode(file)

    torrent_file = contents
    piece_length = torrent_file['info']['piece length']
    pieces = torrent_file['info']['pieces']
    raw_info_hash = bencode(torrent_file['info'])
    info_hash = hashlib.sha1(raw_info_hash).digest()
    number_of_pieces = math.ceil(0 / piece_length)
    print("PIECE LENGTH: ", number_of_pieces)
    print("HASH: ", info_hash.hex())

load_from_path('D:/CN_Ass/input/big-buck-bunny.torrent')