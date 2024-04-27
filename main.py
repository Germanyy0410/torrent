import json
import peer
import os
from bcoding import bdecode, bencode
import hashlib

def get_input_path(file_name):
    return (os.path.dirname(os.path.realpath(__file__)) + '/input/' + file_name).replace('\\', '/')

def get_torrent_path(file_name):
    return get_input_path(file_name) + '/' + file_name + '.torrent'

#* ================================ TORRENT ===============================
# def read_torrent(torrent_file_path):
#     with open(torrent_file_path, 'rb') as torrent_file:
#         torrent_data = torrent_file.read()

#         # Giải mã dữ liệu bằng bencode
#         decoded_data = bdecode(torrent_data)

#         info_hash = hashlib.sha1(bencode(decoded_data['info'])).digest()

#         # Tính toán số lượng phần (pieces)
#         piece_length = decoded_data['info']['piece length']
#         total_length = decoded_data['info']['length']

#         # Tính toán số lượng phần và phần còn dư
#         num_pieces = total_length // piece_length
#         if total_length % piece_length != 0:
#             num_pieces += 1

#         # Trích xuất thông tin cần thiết từ dữ liệu giải mã
#         torrent_info = {
#             'name': decoded_data['info']['name'],
#             'info_hash': info_hash.hex(),
#             'piece_length': piece_length,
#             'total_length': total_length,
#             'num_pieces': num_pieces,
#             'pieces': decoded_data['info']['pieces'],
#             'announce': decoded_data['announce']
#         }

#     return torrent_info


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


def get_total_file_size(torrent_info):
    file_lengths = torrent_info.get('length', [])
    if isinstance(file_lengths, int):
        file_lengths = [file_lengths]

    # Tính tổng kích thước các file
    total_size = sum(file_lengths)

    if total_size >= 1024:
        kb_value = total_size / 1024
        if kb_value >= 1024:
            mb_value = kb_value / 1024
            return str(round(mb_value, 2)) + "MB"
        else:
            return str(round(kb_value, 2)) + "KB"
    else:
        return str(round(total_size, 2)) + "Bytes"

    return total_size


# TODO: Calculate hash bytes in each part
def generate_pieces_hash(pieces_bytes):
    hashes = []
    for i in range(0, len(pieces_bytes), 20):
        piece_data = pieces_bytes[i:i+20]
        hashes.append(piece_data)
    return hashes
#* ========================================================================


#* ========================== START APPLICATION ===========================
if __name__ == '__main__':
    os.system('cls')
    # torrent_name = input("Please input file name you want to download: ")
    torrent_name = 'book'
    torrent_info, piece_hashes = read_torrent(get_torrent_path(torrent_name))

    # Load peer(s) information
    with open("peers.json", "r") as file:
        peers = json.load(file)

    # Connect client to peer(s)
    for p in peers.values():
        input_file = peer.Input(torrent_name)
        input_file.piece_hashes = piece_hashes
        input_file.input_size = get_total_file_size(torrent_info)

        peer_pieces = [input["pieces"] for input in p["pieces"]["inputs"] if input["input_name"] == torrent_name][0]

        peer.get_pieces_status(input_file, get_input_path(torrent_name), total_num_pieces=torrent_info["num_pieces"])
        peer.download_file(p, peer_pieces, input_file.pieces, input_file.piece_hashes, torrent_name)
#* ========================================================================
