import json
import peer
import os

def get_input_path(file_name):
    return (os.path.dirname(os.path.realpath(__file__)) + '/input/' + file_name).replace('\\', '/')


torrent_name = input("Please input file name you want to download: ")

# Load peers information
with open("peers.json", "r") as file:
    peers = json.load(file)

#* ======================= CONNECT CLIENT TO PEER(S) ======================
for p in peers.values():
    input_file = peer.Input(torrent_name)
    peer.get_chunk_status(input_file, get_input_path(torrent_name))
    peer.download_file(p["ip"], p["port"], p["path"], input_file.chunks, torrent_name)
#* ========================================================================