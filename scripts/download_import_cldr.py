#!/usr/bin/env python3

import contextlib
import hashlib
import os
import shutil
import subprocess
import sys
import zipfile
from urllib.request import Request, urlopen

URL = 'https://unicode.org/Public/cldr/47/cldr-common-47.zip'
FILENAME = 'cldr-common-47.0.zip'
# Via https://unicode.org/Public/cldr/45/hashes/SHASUM512.txt
FILESUM = '3b1eb2a046dae23cf16f611f452833e2a95affb1aa2ae3fa599753d229d152577114c2ff44ca98a7f369fa41dc6f45b0d7a6647653ca79694aacfd3f3be59801'


def reporthook(bytes_transmitted, total_size):
    cols = shutil.get_terminal_size().columns
    buffer = 6
    percent = float(bytes_transmitted) / (total_size or 1)
    done = int(percent * (cols - buffer))
    bar = ('=' * done).ljust(cols - buffer)
    sys.stdout.write(f'\r{bar}{int(percent * 100): 4d}%')
    sys.stdout.flush()


def log(message):
    sys.stderr.write(f'{message}\n')


def download_file(url, dest_path, reporthook=None):
    request = Request(url, headers={'User-Agent': 'babel-cldr-downloader (https://babel.pocoo.org/)'})
    with urlopen(request) as response:
        total_size = int(response.headers.get('Content-Length', 0))
        log(f"Downloading {url} to {dest_path}: {total_size // 1024} KiB")
        block_count = 0
        with open(dest_path, 'wb') as out_file:
            while True:
                block = response.read(262144)
                if not block:
                    break
                out_file.write(block)
                block_count += 1
                if reporthook:
                    reporthook(out_file.tell(), total_size)


def is_good_file(filename):
    if not os.path.isfile(filename):
        log(f"Local copy '{filename}' not found")
        return False
    h = hashlib.sha512()
    with open(filename, 'rb') as f:
        while True:
            blk = f.read(262144)
            if not blk:
                break
            h.update(blk)
        digest = h.hexdigest()
        if digest != FILESUM:
            raise RuntimeError(f'Checksum mismatch: {digest!r} != {FILESUM!r}')
        else:
            return True


def main():
    scripts_path = os.path.dirname(os.path.abspath(__file__))
    repo = os.path.dirname(scripts_path)
    cldr_dl_path = os.path.join(repo, 'cldr')
    cldr_path = os.path.join(repo, 'cldr', os.path.splitext(FILENAME)[0])
    zip_path = os.path.join(cldr_dl_path, FILENAME)
    changed = False
    show_progress = (False if os.environ.get("BABEL_CLDR_NO_DOWNLOAD_PROGRESS") else sys.stdout.isatty())

    while not is_good_file(zip_path):
        tmp_path = f"{zip_path}.tmp"
        download_file(URL, tmp_path, (reporthook if show_progress else None))
        os.replace(tmp_path, zip_path)
        changed = True
        print()
    common_path = os.path.join(cldr_path, 'common')

    if changed or not os.path.isdir(common_path):
        if os.path.isdir(common_path):
            log(f"Deleting old CLDR checkout in '{cldr_path}'")
            shutil.rmtree(common_path)

        log(f"Extracting CLDR to '{cldr_path}'")
        with contextlib.closing(zipfile.ZipFile(zip_path)) as z:
            z.extractall(cldr_path)

    subprocess.check_call([
        sys.executable,
        os.path.join(scripts_path, 'import_cldr.py'),
        common_path,
        *sys.argv[1:],
    ])


if __name__ == '__main__':
    main()
