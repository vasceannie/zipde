import csv
from zipfile import ZipFile
import os
import tkinter as tk
from tkinter import filedialog
import io

def list_zip_contents():
    zip_dir_path = filedialog.askdirectory(title="Select Directory Containing ZIP Files")
    if not zip_dir_path:
        print("No directory selected. Exiting.")
        return

    with open('zip_contents.csv', 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['Level', 'Name', 'Type'])

        def get_file_extension(file_path):
            _, extension = os.path.splitext(file_path)
            return extension[1:].lower() if extension else "No extension"

        def traverse_zip(zip_ref, level, prefix=''):
            for info in zip_ref.infolist():
                if info.is_dir():
                    continue
                file_name = info.filename
                file_type = get_file_extension(file_name)
                full_path = os.path.join(prefix, file_name)
                csvwriter.writerow([level, full_path, file_type])

                if file_type == 'zip':
                    with zip_ref.open(info) as inner_zip_file:
                        inner_zip_data = io.BytesIO(inner_zip_file.read())
                        with ZipFile(inner_zip_data) as inner_zip_ref:
                            traverse_zip(inner_zip_ref, level + 1, full_path)

        def traverse_directory(directory, level=0, prefix=''):
            for item in os.listdir(directory):
                item_path = os.path.join(directory, item)
                relative_path = os.path.join(prefix, item)
                
                if os.path.isfile(item_path):
                    file_type = get_file_extension(item_path)
                    csvwriter.writerow([level, relative_path, file_type])
                    
                    if file_type == 'zip':
                        with ZipFile(item_path, 'r') as zip_ref:
                            traverse_zip(zip_ref, level + 1, relative_path)
                elif os.path.isdir(item_path):
                    csvwriter.writerow([level, relative_path, "Directory"])
                    traverse_directory(item_path, level + 1, relative_path)

        traverse_directory(zip_dir_path)

    print(f"Contents have been written to zip_contents.csv")

# Example usage
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    list_zip_contents()
