import os

def split_file(input_file, part_size, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    file_name = os.path.splitext(os.path.basename(input_file))[0]  # Extracting the file name without extension

    with open(input_file, 'rb') as f:
        part_number = 0
        while True:
            data = f.read(part_size)
            if not data:
                break
            part_number += 1
            output_file = os.path.join(output_dir, f'{part_number}_{file_name}.part')
            with open(output_file, 'wb') as part:
                part.write(data)

    print(f"File '{input_file}' has been split into {part_number} parts in '{output_dir}'.")

def merge_files(input_dir, output_file):
    parts = [part for part in os.listdir(input_dir) if part.endswith('.part')]  # Only select part files
    parts.sort(key=lambda x: int(x.split('_')[0]))  # Sort the parts numerically

    with open(output_file, 'wb') as f:
        for part in parts:
            part_path = os.path.join(input_dir, part)
            with open(part_path, 'rb') as p:
                data = p.read()
                f.write(data)

    print(f"The parts in directory '{input_dir}' have been merged into the file '{output_file}'.")

input_file = 'D:/CN_Ass/input/book/book.pdf'  # Path to the input file
part_size = 2 * 1024 * 1024  # Size of each part, e.g. 2 MB
output_directory = 'input/book'  # Output directory where parts will be saved
split_file(input_file, part_size, output_directory)

input_directory = 'D:/CN_Ass/input/book'  # Directory containing the parts
output_file = 'D:/CN_Ass/input/book/book_merged.pdf'  # Output file after merging
merge_files(input_directory, output_file)