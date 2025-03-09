import os
import shutil

def move_csv_files(source_folder, destination_folder):
    files = os.listdir(source_folder)

    for file in files:
        if file.lower().endswith(".csv"):
            os.makedirs(destination_folder, exist_ok=True)
            source_path = os.path.join(source_folder, file)
            destination_path = os.path.join(destination_folder, file)
            shutil.move(source_path, destination_path)
            print(f"File {file} moved to {destination_folder}")
