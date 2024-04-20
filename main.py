import json
import peer
import os

with open("peers.json", "r") as file:
    peers = json.load(file)

download_file_name = input("User: ")
peer_path = '/home/germanyy0410/cn/torrent/input/' + download_file_name

def get_input_path(file_name):
    return (os.path.dirname(os.path.realpath(__file__)) + '/input/' + file_name).replace('\\', '/')

for p in peers.values():
    input_file = peer.Input(download_file_name)
    peer.get_chunk_status(input_file, get_input_path(download_file_name))
    peer.download_file(p["ip"], p["port"], peer_path, input_file.chunks, download_file_name)