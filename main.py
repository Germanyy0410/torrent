import json
import peer
import os
from bcoding import bdecode, bencode

def get_input_path(file_name):
    return (os.path.dirname(os.path.realpath(__file__)) + '/input/' + file_name).replace('\\', '/')

def get_torrent_path(file_name):
    return get_input_path(file_name) + '/' + file_name + '.torrent'

#* ================================ TORRENT ===============================
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
            'length': decoded_data['info']['length'],
            'pieces': decoded_data['info']['pieces'],
            'announce': decoded_data['announce']
        }

    return torrent_info



# TODO: Calculate hash bytes in each part
def generate_pieces_hash(pieces_bytes):
    hashes = []
    for i in range(0, len(pieces_bytes), 20):
        piece_data = pieces_bytes[i:i+20]
        hashes.append(piece_data)
    return hashes
#* ========================================================================


#* ========================== START APPLICATION ===========================
torrent_name = input("Please input file name you want to download: ")
torrent_info = read_torrent(get_torrent_path(torrent_name))
piece_hashes = generate_pieces_hash(torrent_info['pieces'])

#! Load peer(s) information
with open("peers.json", "r") as file:
    peers = json.load(file)

#! Connect client to peer(s)
for p in peers.values():
    input_file = peer.Input(torrent_name)
    input_file.piece_hashes = piece_hashes

    peer.get_pieces_status(input_file, get_input_path(torrent_name))
    peer.download_file(p["ip"], p["port"], p["path"], input_file.pieces, input_file.piece_hashes, torrent_name)


#* ========================================================================
