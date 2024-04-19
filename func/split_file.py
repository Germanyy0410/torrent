import os

def split_file(input_file, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    total_size = os.path.getsize(input_file)
    part_size = total_size // 4  # Calculate the part size to split into 4 parts

    file_name = os.path.splitext(os.path.basename(input_file))[0] # Extracting the file name without extension

    with open(input_file, 'rb') as f:
        part_number = 0
        while part_number < 4:
            data = f.read(part_size)
            if not data:
                break
            part_number += 1
            output_file = os.path.join(output_dir, f'{part_number}_{file_name}.part')  # Adjust filename format
            with open(output_file, 'wb') as part:
                part.write(data)

    print(f"File '{input_file}' has been split into {part_number} parts in '{output_dir}'.")

def merge_files(input_dir, output_file):
    parts = [part for part in os.listdir(input_dir) if part.endswith('.part')]  # Only select part files
    parts.sort(key=lambda x: int(x.split('_')[0])) # Sort the parts numerically

    with open(output_file, 'wb') as f:
        for part in parts:
            part_path = os.path.join(input_dir, part)
            with open(part_path, 'rb') as p:
                data = p.read()
                f.write(data)

    print(f"The parts in directory '{input_dir}' have been merged into the file '{output_file}'.")

input_file = 'D:/CN_Ass/input/excel/excel.csv'  # Path to the input file
output_directory = 'input/excel'  # Output directory where parts will be saved
split_file(input_file, output_directory)

input_directory = 'D:/CN_Ass/input/excel'  # Directory containing the parts
output_file = 'D:/CN_Ass/input/excel/excel_merged.csv'  # Output file after merging
merge_files(input_directory, output_file)