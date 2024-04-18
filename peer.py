import requests # type: ignore
import os
from dotenv import load_dotenv # type: ignore
from datetime import datetime
import socket

load_dotenv()

def get_time():
  current_time = datetime.now()
  formatted_time = current_time.strftime("%d/%m %H:%M:%S")
  return formatted_time

def get_ip():
  hostname = socket.gethostname()
  ip = socket.gethostbyname(hostname)
  return ip

def connect_to_tracker():
  torrent_info = {
    "info_hash": "dd8255ecdc7ca55fb0bbf81323d87062db1f6d1c",
    "peer_id": "Ubuntu " + get_time(),
    "port": 54321,  # Port của peer trên Ubuntu
    "ip": get_ip(),
    "event": "started"
  }
  response = requests.get("http://" + os.environ['CURRENT_IP'] + ":8080/announce", params=torrent_info)
  return response.json()

if __name__ == "__main__":
  tracker_response = connect_to_tracker()
  print("Tracker response:", tracker_response)
  # Tiếp tục xử lý response để thiết lập kết nối với các peer khác và truyền tải dữ liệu
