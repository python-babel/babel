#!/usr/bin/env python

import os
import sys
import shutil
import zipfile
import urllib
import subprocess


URL = 'http://unicode.org/Public/cldr/1.9.1/core.zip'
FILENAME = 'core-1.9.1.zip'
BLKSIZE = 131072


def main():
    scripts_path = os.path.dirname(os.path.abspath(__file__))
    repo = os.path.dirname(scripts_path)
    cldr_path = os.path.join(repo, 'cldr')
    zip_path = os.path.join(cldr_path, FILENAME)

    if not os.path.isfile(zip_path):
        with open(zip_path, 'wb') as f:
            conn = urllib.urlopen(URL)
            while True:
                buf = conn.read(BLKSIZE)
                if not buf:
                    break
                f.write(buf)
            conn.close()

    common_path = os.path.join(cldr_path, 'common')
    if os.path.isdir(common_path):
        shutil.rmtree(common_path)

    z = zipfile.ZipFile(zip_path)
    z.extractall(cldr_path)
    z.close()

    subprocess.check_call([
        sys.executable,
        os.path.join(scripts_path, 'import_cldr.py'),
        common_path])


if __name__ == '__main__':
    main()
