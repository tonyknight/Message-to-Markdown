import csv
import os
import re
import shutil
from pathlib import Path
import pyheif
from PIL import Image

# Define the path to the top-level message archive directory
archive_path = "/Users/knight/Desktop/Messages copy"

def delete_heic_files(path):
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(".heic") or file.endswith(".HEIC"):
                os.remove(os.path.join(root, file))

def move_and_rename_attachments(file_dir, attachments_path):
    os.makedirs(attachments_path, exist_ok=True)

    for file_path in Path(file_dir).iterdir():
        if file_path.is_file():
            filename = file_path.name
            if not (filename.startswith("Messages -") or filename.startswith(".DS_Store")):
                if filename.lower().endswith(".heic"):
                    try:
                        # Convert HEIC image to JPEG
                        heif_file = pyheif.read(file_path)
                        image = Image.frombytes(
                            heif_file.mode,
                            heif_file.size,
                            heif_file.data,
                            "raw",
                            heif_file.mode,
                            heif_file.stride,
                        )
                        jpg_path = file_path.with_suffix('.jpg')
                        image.save(jpg_path, 'JPEG')
                        file_path = jpg_path

                    except Exception as e:
                        with open(file_dir.joinpath("Errors.txt"), mode='a', encoding='utf-8') as error_file:
                            error_file.write(f"Error processing HEIC file {file_path.name}: {str(e)}\n")

                match = re.match(r'^(\d{4}-\d{2}-\d{2}\s\d{2}\s\d{2}\s\d{2})\s-\s(.*?)\s-\s(.+)$', file_path.name)
                if match:
                    date = match.group(1)
                    sender = match.group(2)
                    original_name = match.group(3)
                    extension = file_path.suffix
                    new_filename = original_name
                    counter = 1
                    while attachments_path.joinpath(new_filename).exists():
                        new_filename = f"{os.path.splitext(original_name)[0]} ({counter}){extension}"
                        counter += 1
                    new_path = attachments_path.joinpath(new_filename)
                    shutil.move(str(file_path), str(new_path))

                else:
                    error_file_path = file_dir.joinpath("Errors.txt")
                    with open(error_file_path, mode='a', encoding='utf-8') as error_file:
                        error_file.write(f"{filename}\n")


def format_message(row, attachments_path, file_dir):
    if row['Type'] == 'Outgoing':
        sender = 'Tony Knight'
    else:
        sender = row['Sender Name']
    date = row['Message Date']
    message = row['Text']
    attachment = row['Attachment']

    if attachment:
        attachment_newname = os.path.basename(attachment)
        attachment_newpath = attachments_path.joinpath(attachment_newname)
        attachment_relative_path = os.path.relpath(attachment_newpath, file_dir)

        # Check if the attachment is a HEIC file, and if so, change the link to point to the corresponding JPG file
        if attachment_newname.endswith(".heic") or attachment_newname.endswith(".HEIC"):
            jpg_newname = attachment_newname[:-5] + ".jpg"
            jpg_newpath = attachments_path.joinpath(jpg_newname)
            jpg_relative_path = os.path.relpath(jpg_newpath, file_dir)
            attachment_text = f"![{jpg_newname}]({jpg_relative_path})"
        else:
            attachment_text = f"![{attachment_newname}]({attachment_relative_path})"

        message += f"\n\n{attachment_text}\n\n"

    if sender == 'Tony Knight':
        return f'> [!tldr] {sender} {date}\n{message}\n\n'
    else:
        return f'> [!cite] {sender} {date}\n{message}\n\n'


def process_directory(directory):
    csv_files = list(directory.glob('*.csv'))
    num_files = len(csv_files)
    print(f"Processing {num_files} files in {directory}...")

    for i, csv_file in enumerate(csv_files, start=1):
        file_dir = csv_file.parent
        attachments_path = file_dir.joinpath("Attachments")
        move_and_rename_attachments(file_dir, attachments_path)  # Call the move_and_rename_attachments function

        # Call the convert_to_markdown function, passing the relative Attachments folder path and file directory
        convert_to_markdown(csv_file, attachments_path, file_dir)

        print(f"Processed file {i} of {num_files}")

    print(f"Finished processing files in {directory}\n")


def convert_to_markdown(csv_file, attachments_path, file_dir):
    markdown_path = os.path.join(file_dir, f"{os.path.splitext(csv_file.name)[0]}.md")

    with open(csv_file, mode='r', encoding='utf-8-sig') as csv_file, \
            open(markdown_path, mode='w', encoding='utf-8') as markdown_file:
        reader = csv.DictReader(csv_file)

        for row in reader:
            # Pass the relative Attachments folder path and file directory to the format_message function
            markdown_file.write(format_message(row, attachments_path, file_dir))


def main():
    archive_dir = Path(archive_path)
    for directory in archive_dir.iterdir():
        if directory.is_dir():
            process_directory(directory)
    delete_heic_files(archive_dir)


if __name__ == '__main__':
    main()
