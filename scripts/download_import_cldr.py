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

# In CLDR 49, the common zip no longer contains the locales below Basic
# coverage. See: https://cldr.unicode.org/downloads/cldr-49#migration. The
# stated plan is to remove all locales below Basic coverage in CLDR 50. Since
# presumably some locales will achieve Basic coverage in CLDR 50, we should keep
# all the existing below-Basic coverage locales as is until CLDR 50 makes it
# official.
#
# The below-Basic locales have been moved to a separate file
# ("cldr-exemplars-delta-49.zip"). This file however contains also ~1500 files
# from the CLDR repository's `exemplars/` directory. These are locales that
# don't have data in CLDR and were never available in Babel. We only want to
# merge below-Basic locales with the common data while keeping the exemplars out.
# To do so, we generate an explicit list of all the below-Basic locales.
#
# To regnerate the list, run:
#
#   git clone --depth 1 --branch release-49 --filter=blob:none --no-checkout https://github.com/unicode-org/cldr
#   comm -13 <(unzip -Z1 cldr-common-49.zip 'common/main/*.xml' | sort) \
#            <(git -C cldr ls-tree --name-only release-49 common/main/ | grep '\.xml$' | sort) \
#     | sed 's|common/main/||; s|\.xml$||'
#
BELOW_BASIC_LOCALES = frozenset(
    [
        'aa',
        'aa_DJ',
        'aa_ER',
        'aa_ET',
        'ab',
        'ab_GE',
        'an',
        'an_ES',
        'ann',
        'ann_NG',
        'apc',
        'apc_SY',
        'arn',
        'arn_CL',
        'ary',
        'ary_MA',
        'az_Arab',
        'az_Arab_IQ',
        'az_Arab_IR',
        'az_Arab_TR',
        'bal',
        'bal_Arab',
        'bal_Arab_PK',
        'bew',
        'bew_ID',
        'bgn',
        'bgn_AE',
        'bgn_AF',
        'bgn_IR',
        'bgn_OM',
        'bgn_PK',
        'blt',
        'blt_VN',
        'bm_Nkoo',
        'bm_Nkoo_ML',
        'bqi',
        'bqi_IR',
        'brh',
        'brh_PK',
        'bss',
        'bss_CM',
        'byn',
        'byn_ER',
        'cad',
        'cad_US',
        'cch',
        'cch_NG',
        'cho',
        'cho_US',
        'cic',
        'cic_US',
        'co',
        'co_FR',
        'cu',
        'cu_RU',
        'dv',
        'dv_MV',
        'en_Dsrt',
        'en_Dsrt_US',
        'en_Shaw',
        'en_Shaw_GB',
        'frr',
        'frr_DE',
        'gez',
        'gez_ER',
        'gez_ET',
        'gn',
        'gn_PY',
        'ha_Arab',
        'ha_Arab_NG',
        'ha_Arab_SD',
        'hnj',
        'hnj_Hmnp',
        'hnj_Hmnp_US',
        'hrx',
        'hrx_BR',
        'ht',
        'ht_HT',
        'io',
        'io_001',
        'isv',
        'isv_Cyrl',
        'isv_Cyrl_001',
        'isv_Latn',
        'isv_Latn_001',
        'iu',
        'iu_CA',
        'iu_Latn',
        'iu_Latn_CA',
        'jbo',
        'jbo_001',
        'kaa',
        'kaa_Cyrl',
        'kaa_Cyrl_UZ',
        'kaa_Latn',
        'kaa_Latn_UZ',
        'kaj',
        'kaj_NG',
        'kcg',
        'kcg_NG',
        'ken',
        'ken_CM',
        'kpe',
        'kpe_GN',
        'kpe_LR',
        'ku_Arab',
        'ku_Arab_IQ',
        'ku_Arab_IR',
        'la',
        'la_VA',
        'ltg',
        'ltg_LV',
        'lzz',
        'lzz_TR',
        'mdf',
        'mdf_RU',
        'mhn',
        'mhn_IT',
        'mic',
        'mic_CA',
        'mn_Mong',
        'mn_Mong_CN',
        'mn_Mong_MN',
        'mni_Mtei',
        'mni_Mtei_IN',
        'moh',
        'moh_CA',
        'mrh',
        'mrh_IN',
        'mrh_MM',
        'ms_Arab',
        'ms_Arab_BN',
        'ms_Arab_MY',
        'mus',
        'mus_US',
        'mww',
        'mww_Hmnp',
        'mww_Hmnp_US',
        'myv',
        'myv_RU',
        'nr',
        'nr_ZA',
        'nv',
        'nv_US',
        'ny',
        'ny_MW',
        'oka',
        'oka_CA',
        'oka_US',
        'osa',
        'osa_US',
        'pap',
        'pap_AW',
        'pap_CW',
        'pi',
        'pi_Latn',
        'pi_Latn_GB',
        'pis',
        'pis_SB',
        'rhg',
        'rhg_Rohg',
        'rhg_Rohg_BD',
        'rhg_Rohg_MM',
        'rif',
        'rif_MA',
        'sat_Deva',
        'sat_Deva_IN',
        'sdh',
        'sdh_IQ',
        'sdh_IR',
        'sgs',
        'sgs_LT',
        'sid',
        'sid_ET',
        'skr',
        'skr_PK',
        'sma',
        'sma_NO',
        'sma_SE',
        'smj',
        'smj_NO',
        'smj_SE',
        'sms',
        'sms_FI',
        'ss',
        'ss_SZ',
        'ss_ZA',
        'ssy',
        'ssy_ER',
        'sus',
        'sus_GN',
        'sus_SL',
        'suz',
        'suz_Deva',
        'suz_Deva_NP',
        'tig',
        'tig_ER',
        'tpi',
        'tpi_PG',
        'trv',
        'trv_TW',
        'trw',
        'trw_PK',
        'ts',
        'ts_ZA',
        've',
        've_ZA',
        'vo',
        'vo_001',
        'wa',
        'wa_BE',
        'wal',
        'wal_ET',
        'wbp',
        'wbp_AU',
        'xdq',
        'xdq_RU',
        'zh_Latn',
        'zh_Latn_CN',
    ],
)


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
            wanted = {f'common/main/{locale}.xml' for locale in BELOW_BASIC_LOCALES}
            members = wanted & set(z.namelist())
            for missing in sorted(wanted - members):
                log(f"Warning: '{missing}' not found in '{EXEMPLARS_FILENAME}'")
            z.extractall(cldr_path, members=sorted(members))

    subprocess.check_call([
        sys.executable,
        os.path.join(scripts_path, 'import_cldr.py'),
        common_path,
        *sys.argv[1:],
    ])


if __name__ == '__main__':
    main()
