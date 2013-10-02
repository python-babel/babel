# -*- coding: utf-8 -*-
"""
    babel.messages.operations
    ~~~~~~~~~~~~~~~~~~~~~~~

    Operations for the message extraction functionality.

    :copyright: (c) 2013 by the Babel Team.
    :license: BSD, see LICENSE for more details.
"""

import os
import logging

from babel.messages.pofile import read_po
from babel.messages.mofile import write_mo


log = logging.getLogger('babel')
log.setLevel(logging.INFO)


def make_po_filename(directory, locale, domain):
    return os.path.join(directory, locale, 'LC_MESSAGES', domain + ".po")


def make_mo_filename(directory, locale, domain):
    return os.path.join(directory, locale, 'LC_MESSAGES', domain + ".mo")


class ConfigureError(Exception):
    pass


def find_compile_files(domain="messages", directory=None, input_file=None,
                       output_file=None, locale=None):

    data_files = []

    # not input_file and not directory or not output_file and not directory
    if not ((input_file or directory) and (output_file or directory)):
        raise ConfigureError('you must specify either the input file or '
                             'the base directory')

    if not input_file:
        if locale:
            data_files.append((
                locale,
                make_po_filename(directory, locale, domain),
                make_mo_filename(directory, locale, domain)
            ))
        else:
            for locale in os.listdir(directory):
                po_file = make_po_filename(directory, locale, domain)
                if os.path.exists(po_file):
                    data_files.append((
                        locale,
                        po_file,
                        make_mo_filename(directory, locale, domain)
                    ))
    else:
        if output_file:
            mo_file = output_file
        else:
            mo_file = make_mo_filename(directory, locale, domain)
        data_files.append((locale, input_file, mo_file))

    if not data_files:
        raise ConfigureError('no message catalogs found')

    return data_files


def calc_statistics(catalog, po_file, log=log):
    translated = 0
    percentage = 0
    catalog_len = len(catalog)
    for message in list(catalog)[1:]:
        if message.string:
            translated += 1

    if catalog_len:
        percentage = translated * 100 // catalog_len
    log.info('%d of %d messages (%d%%) translated in %r',
             translated, catalog_len, percentage, po_file)


def compile_files(data_files, use_fuzzy=False, statistics=False, log=log):
    for locale, po_file, mo_file in data_files:
        with open(po_file, 'r') as infile:
            catalog = read_po(infile, locale)

        if statistics:
            calc_statistics(catalog, po_file, log)

        if catalog.fuzzy and not use_fuzzy:
            log.warn('catalog %r is marked as fuzzy, skipping', po_file)
            continue

        for message, errors in catalog.check():
            for error in errors:
                log.error('error: %s:%d: %s', po_file, message.lineno, error)

        log.info('compiling catalog %r to %r', po_file, mo_file)

        with open(mo_file, 'wb') as outfile:
            write_mo(outfile, catalog, use_fuzzy=use_fuzzy)


def compile_catalog(domain="messages", directory=None, input_file=None,
                    output_file=None, locale=None, use_fuzzy=False,
                    statistics=False, log=log):

    data_files = find_compile_files(
        domain=domain,
        directory=directory,
        input_file=input_file,
        output_file=output_file,
        locale=locale
    )
    compile_files(data_files, use_fuzzy=use_fuzzy, statistics=statistics,
                  log=log)
