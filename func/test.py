import os

def merge_files(input_dir, output_file):
    parts = [part for part in os.listdir(input_dir) if part.endswith('.part')]  # Chọn chỉ các file parts
    parts.sort(key=lambda x: int(x.split('_')[0]))  # Sắp xếp các parts theo số thứ tự

    merged = False
    previous_number = None
    with open(output_file, 'wb') as f:
        for part in parts:
            number = int(part.split('_')[0])
            if previous_number is None or number == previous_number + 1:
                part_path = os.path.join(input_dir, part)
                with open(part_path, 'rb') as p:
                    data = p.read()
                    f.write(data)
                merged = True
                previous_number = number
            else:
                merged = False
                break

    if merged:
        print(f"The parts in directory '{input_dir}' have been merged into the file '{output_file}'.")
    else:
        os.remove(output_file)
        print("Cannot merge the parts due to discontinuous numbering.")
        # Đối với trường hợp không merge, bạn có thể thêm các xử lý khác ở đây hoặc trả về thông báo lỗi.
        # Ví dụ: raise ValueError("Cannot merge the parts due to discontinuous numbering.")
input_directory = 'D:/CN_Ass/input/book'  # Directory containing the parts
output_file = 'D:/CN_Ass/input/book/book_merged.pdf'  # Output file after merging
merge_files(input_directory, output_file)