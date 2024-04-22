import json
import peer
import os
from bcoding import bdecode, bencode

def get_input_path(file_name):
    return (os.path.dirname(os.path.realpath(__file__)) + '/input/' + file_name).replace('\\', '/')


#* ================================ TORRENT ===============================
# def load_from_path(path):
#     with open(path, 'rb') as file:
#         contents = bdecode(file)
#     print(contents)

# load_from_path('D:/CN_Ass/input/big-buck-bunny.torrent')
#* ========================================================================


# torrent_name = input("Please input file name you want to download: ")

# # Load peers information
# with open("peers.json", "r") as file:
#     peers = json.load(file)

# #* ======================= CONNECT CLIENT TO PEER(S) ======================
# for p in peers.values():
#     input_file = peer.Input(torrent_name)
#     peer.get_pieces_status(input_file, get_input_path(torrent_name))
#     peer.download_file(p["ip"], p["port"], p["path"], input_file.pieces, torrent_name)
# #* ========================================================================

new = peer.InputData()
peer.get_all_input_pieces_status(new, 'D:/CN_Ass/input/')
json_data = json.dumps(new.to_dict())