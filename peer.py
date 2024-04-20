import requests # type: ignore
import os
from dotenv import load_dotenv # type: ignore
from datetime import datetime
import socket
import peer_to_peer

load_dotenv()

def get_time():
  current_time = datetime.now()
  formatted_time = current_time.strftime("%d/%m %H:%M:%S")
  return formatted_time

# ============================= PEER TO PEER =============================

# =========================================================================


# ======================== CONNECT PEER TO TRACKER ========================
def get_ip():
  hostname = socket.gethostname()
  ip = socket.gethostbyname(hostname)
  return ip

def get_input_dir():
  return os.path.dirname(os.path.realpath(__file__)) + '/input/'

def connect_to_tracker():
  torrent_info = {
    "info_hash": "dd8255ecdc7ca55fb0bbf81323d87062db1f6d1c",
    "peer_id": "Ubuntu " + get_time(),
    "port": 1234,  # Port của peer trên Ubuntu
    "ip": get_ip(),
    "tracked_chunks": peer_to_peer.get_all_input_chunks_status(get_input_dir()),  # TODO: <-- Add path here
    "event": "started"
  }
  response = requests.get("http://" + os.environ['CURRENT_IP'] + ":8080/announce", params=torrent_info)
  return response.json()
# ========================================================================



if __name__ == "__main__":
  tracker_response = connect_to_tracker()
  print("Tracker response:", tracker_response)
  print(os.path.dirname(os.path.realpath(__file__)))
  # Tiếp tục xử lý response để thiết lập kết nối với các peer khác và truyền tải dữ liệu

