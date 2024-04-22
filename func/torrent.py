from bcoding import bdecode, bencode
import hashlib
import json
import math
import bencodepy

def create_torrent(file_path, tracker_url, piece_length=512 * 1024):
    # Đọc nội dung của tập tin
    with open(file_path, 'rb') as f:
        file_data = f.read()

    # Tính toán độ dài của tập tin
    file_size = len(file_data)

    # Tính toán số lượng phần
    num_pieces = -(-file_size // piece_length)

    # Tính toán hash của từng phần và sắp xếp chúng thành một danh sách
    piece_hashes = [hashlib.sha1(file_data[i:i+piece_length]).digest() for i in range(0, file_size, piece_length)]

    # Tạo thông tin của torrent
    torrent_info = {
        'info': {
            'name': file_path,
            'piece length': piece_length,
            'length': file_size,
            'pieces': b''.join(piece_hashes)
        },
        'announce': tracker_url
    }

    # Mã hóa thông tin của torrent bằng Bencoding
    torrent_data = bencode(torrent_info)

    # Lưu dữ liệu của torrent vào file
    with open(file_path.split('.')[0] + '.torrent', 'wb') as torrent_file:
        torrent_file.write(torrent_data)

create_torrent('D:/CN_Ass/input/video/video.mkv', 'http://192.168.1.8:8080/announce')

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

# torrent_file_path = 'D:/CN_Ass/input/book/book.pdf.torrent'
# torrent_info = read_torrent(torrent_file_path)

# pieces_bytes = torrent_info['pieces']  # Lấy chuỗi hash từ dữ liệu torrent
# piece_length = torrent_info['piece_length']  # Độ dài của mỗi phần

# # Duyệt qua từng phần của chuỗi hash và in ra giá trị hash của từng phần
# for i in range(0, len(pieces_bytes), 20):  # Mỗi giá trị hash có độ dài 20 bytes
#     hash_value = pieces_bytes[i:i+20]  # Lấy một phần của chuỗi hash
#     print("Hash của phần", i // 20 + 1, ":", hash_value.hex())


# def calculate_piece_hash(piece_data):
#     sha1 = hashlib.sha1()  # Khởi tạo đối tượng hash SHA-1
#     sha1.update(piece_data)  # Cập nhật dữ liệu vào đối tượng hash
#     return sha1.digest()  # Trả về giá trị hash dưới dạng bytes

# def read_file(file_path):
#     with open(file_path, 'rb') as f:
#         byte_data = f.read()
#     return byte_data

# piece_data = read_file('D:/CN_Ass/input/book/12_book.part')
# piece_hash = calculate_piece_hash(piece_data)
# print("Giá trị hash của phần file:", piece_hash.hex())

# def compare_strings(str1, str2):
#     if str1 == str2:
#         return "Hai chuỗi giống nhau."
#     else:
#         return "Hai chuỗi không giống nhau."

# # Sử dụng hàm để so sánh hai chuỗi
# string1 = "6e67e85324f0bdabdeb0c929fa0e3fa2a2948916"
# string2 = "6e67e85324f0bdabdeb0c929fa0e3fa2a2948916"

# result = compare_strings(string1, string2)
# print(result)