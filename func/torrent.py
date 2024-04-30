from bcoding import bdecode, bencode
import hashlib
import json
import math
import bencodepy
import os

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
            'announce': decoded_data['announce']
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
                file_num_pieces = file_info['num_pieces']
                file_pieces = file_info['pieces']
                file_name = file_info['name']
                files.append({'path': file_path, 'name': file_name, 'length': file_length, 'num_pieces': file_num_pieces, 'pieces': file_pieces})

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

directory_path = 'D:/CN_Ass/output/books'
tracker_url = 'http:/10.46.153.20:8080/announce'
# directory_path = 'D:/CN_Ass/input/videos'
# tracker_url = 'http:/192.168.1.6:8080/announce'

create_torrent(directory_path, tracker_url)

# # Đọc thông tin từ file torrent và in ra thông tin của mỗi file
# torrent_info, file_piece_hashes = read_torrent(directory_path + '/videos.torrent')

# print("All piece hashes:", type(file_piece_hashes))