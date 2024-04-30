import os

def split_file(input_file, output_dir, part_size=512 * 1024):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    file_name = os.path.splitext(os.path.basename(input_file))[0]  # Extracting the file name without extension
    arr = []
    with open(input_file, 'rb') as f:
        part_number = 0
        while True:
            data = f.read(part_size)
            if not data:
                break
            part_number += 1
            output_file = os.path.join(output_dir, f'{file_name}_{part_number}.part')  # Adjust filename format
            arr.append(data)
            with open(output_file, 'wb') as part:
                part.write(data)

    print(f"File '{input_file}' has been split into {part_number} parts in '{output_dir}'.")
    return arr


def merge_files(input_dir, output_file, arr):
    parts = [part for part in os.listdir(input_dir) if part.endswith('.part')]  # Only select part files
    parts.sort(key=lambda x: int(x.split('_')[0])) # Sort the parts numerically

    with open(output_file, 'wb') as f:
        for part in arr:
            # part_path = os.path.join(input_dir, part)
            # with open(part_path, 'rb') as p:
            #     data = p.read()
            #     f.write(data)
            f.write(part)

    print(f"The parts in directory '{input_dir}' have been merged into the file '{output_file}'.")

input_file = 'D:/CN_Ass/output/books/A.pdf'  # Path to the input file
output_directory = 'input/books/parts'  # Output directory where parts will be saved
# input_file = f'D:/CN_Ass/input/videos/video.mkv'
# output_directory = 'input/videos/parts'  # Output directory where parts will be saved
arr = split_file(input_file, output_directory, part_size=512 * 1024)

# input_directory = 'D:/CN_Ass/input/video'  # Directory containing the parts
# output_file = 'D:/CN_Ass/input/video/video_merged.mkv'  # Output file after merging
# merge_files(input_directory, output_file, arr)

# def calculate_chunk():