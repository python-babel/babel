#!/usr/bin/env python3

import contextlib
import hashlib
import os
import shutil
import subprocess
import sys
import zipfile
from urllib.request import Request, urlopen

COMMON_URL = 'https://unicode.org/Public/cldr/49/cldr-common-49.zip'
COMMON_FILENAME = 'cldr-common-49.zip'
EXEMPLARS_URL = 'https://unicode.org/Public/cldr/49/cldr-exemplars-delta-49.zip'
EXEMPLARS_FILENAME = 'cldr-exemplars-delta-49.zip'
# Via https://unicode.org/Public/cldr/49/hashes/SHASUM512.txt (core.zip; see https://unicode-org.atlassian.net/browse/CLDR-19388)
COMMON_FILESUM = 'c704a2baf9ce4e28f40e242f8b2fbd0123579bb2c56daaaf8a92d72abd02485a1f60095c3cc4fe89eaf2d5c9f5fd07954c2eaee88839f97e18b1ff37cd62e2d8'
EXEMPLARS_FILESUM = '8c0331f4927833499d24a716e2d072a87ae169098d41886d3ae51028e4f5033f8c139339c2c8b073b59da8431663c91ed15d24a61aaa78305994e22326521836'


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


def is_good_file(filename, filesum):
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
        if digest != filesum:
            raise RuntimeError(f'Checksum mismatch: {digest!r} != {filesum!r}')
        else:
            return True


def main():
    scripts_path = os.path.dirname(os.path.abspath(__file__))
    repo = os.path.dirname(scripts_path)
    cldr_dl_path = os.path.join(repo, 'cldr')
    cldr_path = os.path.join(repo, 'cldr', os.path.splitext(COMMON_FILENAME)[0])
    common_zip_path = os.path.join(cldr_dl_path, COMMON_FILENAME)
    exemplars_zip_path = os.path.join(cldr_dl_path, EXEMPLARS_FILENAME)
    changed = False
    show_progress = (False if os.environ.get("BABEL_CLDR_NO_DOWNLOAD_PROGRESS") else sys.stdout.isatty())

    while not is_good_file(common_zip_path, COMMON_FILESUM):
        tmp_path = f"{common_zip_path}.tmp"
        download_file(COMMON_URL, tmp_path, (reporthook if show_progress else None))
        os.replace(tmp_path, common_zip_path)
        changed = True
        print()
    while not is_good_file(exemplars_zip_path, EXEMPLARS_FILESUM):
        tmp_path = f"{exemplars_zip_path}.tmp"
        download_file(EXEMPLARS_URL, tmp_path, (reporthook if show_progress else None))
        os.replace(tmp_path, exemplars_zip_path)
        changed = True
        print()
    common_path = os.path.join(cldr_path, 'common')

    if changed or not os.path.isdir(common_path):
        if os.path.isdir(common_path):
            log(f"Deleting old CLDR checkout in '{cldr_path}'")
            shutil.rmtree(common_path)

        log(f"Extracting CLDR to '{cldr_path}'")
        with contextlib.closing(zipfile.ZipFile(common_zip_path)) as z:
            z.extractall(cldr_path)
        with contextlib.closing(zipfile.ZipFile(exemplars_zip_path)) as z:
            z.extractall(cldr_path)

    subprocess.check_call([
        sys.executable,
        os.path.join(scripts_path, 'import_cldr.py'),
        common_path,
        *sys.argv[1:],
    ])


if __name__ == '__main__':
    main()
