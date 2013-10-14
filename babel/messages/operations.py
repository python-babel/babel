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
import tempfile
import shutil
from datetime import datetime

from babel.messages.pofile import read_po, write_po
from babel.messages.mofile import write_mo
from babel.messages.extract import extract_from_dir
from babel.util import LOCALTZ
from babel import Locale


log = logging.getLogger('babel')
log.setLevel(logging.INFO)


def make_po_filename(directory, locale, domain):
    return os.path.join(directory, locale, 'LC_MESSAGES', domain + ".po")


def make_mo_filename(directory, locale, domain):
    return os.path.join(directory, locale, 'LC_MESSAGES', domain + ".mo")


def gen_tempname(filename):
    return os.path.join(
        os.path.dirname(filename),
        tempfile.gettempprefix() + os.path.basename(filename)
    )


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


def init_catalog(input_file, output_file, locale_str, fuzzy=False, width=None,
                 log=log):

    locale = Locale.parse(locale_str)
    with open(input_file, 'r') as infile:
        # Although reading from the catalog template, read_po must be fed
        # the locale in order to correctly calculate plurals
        catalog = read_po(infile, locale=locale_str)

    catalog.locale = locale
    catalog.revision_date = datetime.now(LOCALTZ)
    catalog.fuzzy = fuzzy
    log.info('creating catalog %r based on %r', output_file, input_file)

    with open(output_file, 'wb') as outfile:
        write_po(outfile, catalog, width=width)


def find_update_files(output_dir=None, output_file=None, locale=None,
                      domain="messages"):
    po_files = []
    if not output_file:
        if locale:
            po_files.append((
                locale,
                make_po_filename(output_dir, locale, domain)
            ))
        else:
            for locale in os.listdir(output_dir):
                po_file = make_po_filename(output_dir, locale, domain)
                if os.path.exists(po_file):
                    po_files.append((locale, po_file))
    else:
        po_files.append((locale, output_file))

    if not po_files:
        raise ConfigureError('no message catalogs found')

    return po_files


def update_po_files(input_file, po_files, domain="messages", no_fuzzy=False,
                    ignore_obsolete=False, previous=False, width=None,
                    log=log):

    # this is necessary ?
    if not domain:
        domain = os.path.splitext(os.path.basename(input_file))[0]

    with open(input_file, 'U') as infile:
        template = read_po(infile)

    for locale, filename in po_files:
        log.info('updating catalog %r based on %r', filename, input_file)
        with open(filename, 'U') as infile:
            catalog = read_po(infile, locale=locale, domain=domain)

        catalog.update(template, no_fuzzy)

        tmpname = gen_tempname(filename)
        tmpfile = open(tmpname, 'w')
        try:
            with tmpfile:
                write_po(tmpfile, catalog, ignore_obsolete=ignore_obsolete,
                         include_previous=previous, width=width)
        except:
            os.remove(tmpname)
            raise

        try:
            os.rename(tmpname, filename)
        except OSError:
            # We're probably on Windows, which doesn't support atomic
            # renames, at least not through Python
            # If the error is in fact due to a permissions problem, that
            # same error is going to be raised from one of the following
            # operations
            os.remove(filename)
            shutil.copy(tmpname, filename)
            os.remove(tmpname)


def update_catalog(input_file, output_dir=None, output_file=None, locale=None,
                   domain="messages", no_fuzzy=False, ignore_obsolete=False,
                   previous=False, width=None, log=log):

    po_files = find_update_files(output_dir, output_file, locale, domain)

    update_po_files(input_file, po_files, domain=domain, no_fuzzy=no_fuzzy,
                    ignore_obsolete=ignore_obsolete, previous=previous,
                    width=width, log=log)


def _gen_optstr(options):
    optstr = ''
    if options:
        opt_couplestr = ('%s="%s"' % (k, v) for k, v in options.iteritems())
        optstr = ' (%s)' % ', '.join(opt_couplestr)
    return optstr


def _gen_filepath(dirname, filename):
    return os.path.normpath(os.path.join(dirname, filename))


def extract_to_catalog(catalog, data_iterator, keywords, comment_tags,
                       strip_comment_tags, log=log):

    for dirname, method_map, options_map in data_iterator:
        if not os.path.isdir(dirname):
            raise ConfigureError('%r is not a directory' % dirname)

        def callback(filename, method, options):
            if method == 'ignore':
                return
            filepath = _gen_filepath(dirname, filename)
            optstr = _gen_optstr(options)
            log.info('extracting messages from %s%s', filepath, optstr)

        extracted = extract_from_dir(dirname, method_map, options_map,
                                     keywords=keywords,
                                     comment_tags=comment_tags,
                                     callback=callback,
                                     strip_comment_tags=strip_comment_tags)

        # Add extracted strings to catalog
        for filename, lineno, message, comments, context in extracted:
            filepath = _gen_filepath(dirname, filename)
            catalog.add(message, None, [(filepath, lineno)],
                        auto_comments=comments, context=context)
