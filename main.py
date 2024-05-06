from peer import *
import os
from bcoding import bdecode, bencode
import hashlib
import peer
from tracker import *
import requests
from prettytable import PrettyTable

class colors:
    RED = '\033[91m'
    RED_BOLD = '\033[91m\033[1m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'

def get_input_path(file_name):
    return (os.getcwd() + '/input/' + file_name).replace('\\', '/')


def get_output_path(file_name):
    return (os.getcwd() + '/output/' + file_name).replace('\\', '/')


def get_torrent_path(file_name):
    return get_input_path(file_name) + '/' + file_name + '.torrent'


#* ================================ TORRENT ===============================

def create_torrent(directory_path, tracker_url, piece_length=512 * 1024):
    files = []

    for root, _, filenames in os.walk(directory_path):
        for filename in filenames:
            file_path = os.path.join(root, filename)

            with open(file_path, 'rb') as f:
                file_data = f.read()

            file_size = len(file_data)

            num_pieces = -(-file_size // piece_length)

            pieces = []
            for i in range(0, file_size, piece_length):
                piece_data = file_data[i:i+piece_length]
                piece_hash = hashlib.sha1(piece_data).digest()
                piece_size = len(piece_data)
                pieces.append({'hash': piece_hash, 'length': piece_size})

            file_hash = hashlib.sha1(file_data).digest()

            file_info = {
                'path': file_path.replace("\\", "/"),
                'name': file_path.replace("\\", "/").split('/')[-1],
                'length': file_size,
                'pieces': pieces,
                'num_pieces': num_pieces,
                'file_hash': file_hash
            }
            files.append(file_info)

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
    torrent_data = bencode(torrent_info)

    torrent_file_path = os.path.join(directory_path, directory_path.split('/')[-1] + '.torrent')
    with open(torrent_file_path, 'wb') as torrent_file:
        torrent_file.write(torrent_data)

    print("\n{} is successfully created.".format(torrent_file_path))


def read_torrent(torrent_file_path):
    with open(torrent_file_path, 'rb') as torrent_file:
        torrent_data = torrent_file.read()

        decoded_data = bdecode(torrent_data)

        torrent_info = {
            'name': decoded_data['info']['name'],
            'piece_length': decoded_data['info']['piece length'],
            'announce': decoded_data['announce'],
            'info_hash': decoded_data['info']['info_hash'],
        }

        file_piece_hashes = {}

        if 'files' in decoded_data['info']:
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

                file_piece_hashes[file_name] = [piece['hash'].hex() for piece in file_pieces]

            torrent_info['files'] = files
        else:
            file_path = torrent_info['name']
            file_name = file_path.split('/')[-1]
            file_length = decoded_data['info']['length']
            file_num_pieces = -(-file_length // torrent_info['piece_length'])
            file_pieces = [{'hash': decoded_data['info']['pieces'][i:i+20], 'length': torrent_info['piece_length']} for i in range(0, len(decoded_data['info']['pieces']), 20)]
            torrent_info['files'] = [{'path': file_path, 'name': file_name, 'length': file_length, 'num_pieces': file_num_pieces, 'pieces': file_pieces}]

            file_piece_hashes[file_name] = [piece['hash'].hex() for piece in file_pieces]

    return torrent_info, file_piece_hashes


def get_torrent_status(torrent_name):
    torrent_info, piece_hashes = read_torrent(get_torrent_path(torrent_name))
    input = peer.Input(torrent_name)
    input.piece_hashes = piece_hashes

    for file in torrent_info["files"]:
        if ".torrent" in file:
            break

        file_path = get_output_path(torrent_name) + "/" + file["name"]
        status = False
        if os.path.exists(file_path):
            status = True
        file_info = peer.File(file["name"], file["length"], file["num_pieces"], status)
        peer.get_pieces_status(file_info, get_input_path(torrent_name) + "/parts/")
        input.files.append(file_info)

    bit_field = {}
    for file in input.files:
        bit_field[file.file_name] = ""
        for piece in file.pieces:
            if piece.status == True:
                bit_field[file.file_name] += "1"
            else:
                bit_field[file.file_name] += "0"

    return input, bit_field


def get_peers_from_tracker():
    response = requests.get("http://" + os.environ['CURRENT_IP'] + ":8080/get_peers")
    return response.json()

#* ========================================================================

def torrent_start(torrent_name):
    os.system("cls")
    torrent_info(torrent_name)
    time.sleep(1)
    torrent_peer()
    time.sleep(1)

    peers = get_peers_from_tracker()
    input, bit_field = get_torrent_status(torrent_name)
    download_torrent(peers, input, torrent_name)
    upload_torrent(peers, input, torrent_name)


def torrent_info(torrent_name):
    torrent_info, piece_hashes = read_torrent(get_torrent_path(torrent_name))
    print("\n•  announce URL: {}".format(torrent_info["announce"]))
    print("•  info hash: {}\n".format(torrent_info["info_hash"].hex()))

    table = PrettyTable([colors.YELLOW + "file" + colors.RESET, colors.YELLOW + "size" + colors.RESET, colors.YELLOW + "no. pieces" + colors.RESET, colors.YELLOW + "file hash" + colors.RESET])
    for file in torrent_info["files"]:
        table.add_row([file["name"], get_piece_size(file["length"]), file["num_pieces"], file["file_hash"].hex()])
    print(table.get_string())


def torrent_show():
    folder_path = os.getcwd() + '/input/'
    torrent_files = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".torrent"):
                torrent_files.append(os.path.join(root, file))

    print("\nList of torrent files:")
    for file in torrent_files:
        print("   |-- {}".format(file.replace("\\", "/")))

    return torrent_files

def torrent_peer():
    print("\nGetting peers from http://" + os.environ['CURRENT_IP'] + ":8080\n")
    table = PrettyTable([colors.YELLOW + 'peer_id' + colors.RESET, colors.YELLOW + 'IP' + colors.RESET, colors.YELLOW + 'Port' + colors.RESET])
    peers = get_peers_from_tracker()

    for peer in peers.values():
        table.add_row([peer["peer_id"], peer["ip"], peer["port"]])
    print(table.get_string())

def torrent_edit_tracker_url(torrent_name, new_tracker_url):
    torrent_file_path = get_torrent_path(torrent_name)
    with open(torrent_file_path, 'rb') as torrent_file:
        torrent_data = torrent_file.read()
        decoded_data = bdecode(torrent_data)

    if 'announce' in decoded_data:
        decoded_data['announce'] = new_tracker_url

        with open(torrent_file_path, 'wb') as torrent_file:
            torrent_file.write(bencode(decoded_data))
        print("Change tracker URL successfully to " + new_tracker_url)
    else:
        print("Torrent file does not contain tracker URL")

#* ========================== START APPLICATION ===========================

input_command = True

def user_input_thread():
    global input_command
    while True:
        user_command = input(colors.GREEN + "\n>> Enter command here: " + colors.RESET)

        if "b-create" in user_command:
            if len(user_command.split(" ")) != 3:
                print (colors.RED_BOLD + "\nSyntax Error: " + colors.RESET + "Command not found")
            else:
                dir_path = user_command.split(" ")[1]
                tracker_url = user_command.split(" ")[2]
                if os.path.exists(dir_path):
                    create_torrent(dir_path, tracker_url)
                else:
                    print("Directory not found, please try again")

        elif "b-show" in user_command:
            if len(user_command.split(" ")) != 1:
                print (colors.RED_BOLD + "\nSyntax Error: " + colors.RESET + "Command not found")
            else:
                torrent_show()

        elif "b-peer" in user_command:
            if len(user_command.split(" ")) != 1:
                print (colors.RED_BOLD + "\nSyntax Error: " + colors.RESET + "Command not found")
            else:
                torrent_peer()


        elif "b-info" in user_command:
            if len(user_command.split(" ")) != 2:
                print (colors.RED_BOLD + "\nSyntax Error: " + colors.RESET + "Command not found")
            else:
                torrent_name = user_command.split(" ")[1]
                torrent_info(torrent_name)

        elif "b-start" in user_command:
            if len(user_command.split(" ")) != 2:
                print (colors.RED_BOLD + "\nSyntax Error: " + colors.RESET + "Command not found")
            else:
                torrent_name = user_command.split(" ")[1]
                torrent_start(torrent_name)

        elif "b-help" in user_command:
            if len(user_command.split(" ")) != 1:
                print (colors.RED_BOLD + "\nSyntax Error: " + colors.RESET + "Command not found")
            else:
                print_input_help()

        elif "b-edit" in user_command:
            if (len(user_command.split(" ")) != 3):
                print (colors.RED_BOLD + "\nSyntax Error: " + colors.RESET + "Command not found")
            else:
                torrent_name = user_command.split(" ")[1]
                new_tracker_url = user_command.split(" ")[2]
                torrent_edit_tracker_url(torrent_name, new_tracker_url)

        elif "b-close" in user_command:
            if len(user_command.split(" ")) != 1:
                print (colors.RED_BOLD + "\nSyntax Error: " + colors.RESET + "Command not found")
            else:
                print(colors.YELLOW + "\nWarning: " + colors.RESET +"Closing application...\n")
                break

        else:
            print (colors.RED_BOLD + "\nError: " + colors.RESET + "Command not found")


def print_input_help():
    print("\nSome useful commands you should use:\n")
    print("•  " + colors.BLUE + "b-create <path> <tracker-url>:" + colors.RESET + " Create a .torrent file for the content at the specified path, with the given tracker URL.\n")
    print("•  " + colors.BLUE + "b-edit <torrent-file> <new-tracker-url>:" + colors.RESET + " Modify the announce URL of a .torrent file, providing flexibility in managing torrents efficiently.\n")
    print("•  " + colors.BLUE + "b-show:" + colors.RESET + " Display all managed torrent files, helping you keep track of your torrents easily.\n")
    print("•  " + colors.BLUE + "b-info <torrent-file>:" + colors.RESET + " View metadata associated with a .torrent file, such as file names, sizes, and hash values.\n")
    print("•  " + colors.BLUE + "b-peer:" + colors.RESET + " View all peers that connected to tracker server.\n")
    print("•  " + colors.BLUE + "b-start <torrent-file>:" + colors.RESET + " Start downloading files from the specified .torrent file seamlessly.\n")
    print("•  " + colors.BLUE + "b-help:" + colors.RESET + " View all commands and usages.\n")
    print("•  " + colors.BLUE + "b-close:" + colors.RESET + " Close the application.")


if __name__ == '__main__':
    text_based = """
                                             ___  ___  _____   _____  ___   ___  ___  _  _  _____
                                            | _ )|_ _||_   _| |_   _|/ _ \ | _ \| __|| \| ||_   _|
                                            | _ \ | |   | |     | | | (_) ||   /| _| | .` |  | |
                                            |___/|___|  |_|     |_|  \___/ |_|_\|___||_|\_|  |_|
    """
    os.system("cls")
    print(colors.MAGENTA + text_based + colors.RESET)

    print_input_help()
    input_thread = threading.Thread(target=user_input_thread)
    input_thread.start()

#* ========================================================================
