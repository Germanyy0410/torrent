import requests
import os
from dotenv import load_dotenv # type: ignore

load_dotenv()

def connect_to_tracker():
    torrent_info = {
        "info_hash": "dd8255ecdc7ca55fb0bbf81323d87062db1f6d1c",
        "peer_id": "your_ubuntu_peer_id",
        "port": 54321,  # Port của peer trên Ubuntu
        "event": "started"
    }
    response = requests.get("http://" + os.environ['CURRENT_IP'] + ":8080/announce", params=torrent_info)
    return response.json()

if __name__ == "__main__":
    tracker_response = connect_to_tracker()
    print("Tracker response:", tracker_response)
    # Tiếp tục xử lý response để thiết lập kết nối với các peer khác và truyền tải dữ liệu
