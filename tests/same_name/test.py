import argparse
import os
from io import SEEK_CUR

AR_FILE_NAME_SIZE = 16
AR_SIZE_OFFSET = 32
AR_SIZE_SIZE = 10
AR_FILE_START_OFFSET = 2


def extract_archive(archive_path, destination_path):
    archive = open(archive_path, 'rb')

    global_header = archive.read(8)
    if global_header != '!<arch>\n':
        print(archive_path + ' seems not to be an archive file!')
        exit(1)

    processed_files = dict()

    count = 0
    while True:
        count = count + 1
        ar_file_name_bytes = archive.read(AR_FILE_NAME_SIZE)
        if len(ar_file_name_bytes) == 0:
            break
        ar_file_name_raw = ar_file_name_bytes.rstrip(' ').decode()
        archive.seek(AR_SIZE_OFFSET, SEEK_CUR)
        ar_file_size = int(archive.read(AR_SIZE_SIZE).rstrip(' ').decode())
        if ar_file_name_raw.startswith('#1/'):
            file_name_size = int(ar_file_name_raw.replace('#1/', ''))
            ar_file_size = ar_file_size - file_name_size
            archive.seek(AR_FILE_START_OFFSET, SEEK_CUR)
            ar_file_name = archive.read(file_name_size).rstrip(b'\x00').decode()
        else:
            ar_file_name = ar_file_name_raw.decode()
            archive.seek(AR_FILE_START_OFFSET, SEEK_CUR)
        new_file_name = ""
        if ar_file_name in ['/', '//', '__.SYMDEF']:
            ar_file_name = ""
        else:
            if ar_file_name.endswith('/'):
                ar_file_name = ar_file_name[:-1]
            if ar_file_name in processed_files:
                filename, ext = os.path.splitext(ar_file_name)
                new_file_name = "%s_%d%s" % (filename, processed_files[ar_file_name] + 1, ext)
                processed_files[ar_file_name] = processed_files[ar_file_name] + 1
            else:
                new_file_name = ar_file_name
                processed_files[ar_file_name] = 1

        if new_file_name:
            with open(os.path.join(destination_path, new_file_name), 'wb') as out:
                out.write(archive.read(ar_file_size))
        else:
            archive.seek(ar_file_size, SEEK_CUR)

        if archive.tell() % 2 == 1:
            archive.read(1)

    archive.close()

parser = argparse.ArgumentParser(description='Extract archive files.')
parser.add_argument('--archive', type=str, help='Path to the archive to extract')
parser.add_argument('--destination', type=str, help='Path to the destination')
args = parser.parse_args()

extract_archive(args.archive, args.destination)

