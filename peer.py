import requests # type: ignore
import json

def connect_to_tracker():
    torrent_info = {
        "info_hash": "dd8255ecdc7ca55fb0bbf81323d87062db1f6d1c",
        "peer_id": "your_windows_peer_id",
        "port": 12345,  # Port của peer trên Windows
        "event": "started"
    }
    response = requests.get("http://192.168.0.6:8080", params=torrent_info)
    return response.json()

if __name__ == "__main__":
    tracker_response = connect_to_tracker()
    print("Tracker response:", json.dumps(tracker_response, indent=4))
    # Tiếp tục xử lý response để thiết lập kết nối với các peer khác và truyền tải dữ liệu
