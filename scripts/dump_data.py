#!/usr/bin/env python
#
# Copyright (C) 2007-2011 Edgewall Software, 2013-2025 the Babel team
# All rights reserved.
#
# This software is licensed as described in the file LICENSE, which
# you should have received as part of this distribution. The terms
# are also available at https://github.com/python-babel/babel/blob/master/LICENSE.
#
# This software consists of voluntary contributions made by many
# individuals. For the exact contribution history, see the revision
# history and logs, available at https://github.com/python-babel/babel/commits/master/.

from optparse import OptionParser
from pprint import pprint

from babel.localedata import LocaleDataDict, load


def main():
    parser = OptionParser(usage='%prog [options] locale [path]')
    parser.add_option('--noinherit', action='store_false', dest='inherit',
                      help='do not merge inherited data into locale data')
    parser.add_option('--resolve', action='store_true', dest='resolve',
                      help='resolve aliases in locale data')
    parser.set_defaults(inherit=True, resolve=False)
    options, args = parser.parse_args()
    if len(args) not in (1, 2):
        parser.error('incorrect number of arguments')

    data = load(args[0], merge_inherited=options.inherit)
    if options.resolve:
        data = LocaleDataDict(data)
    if len(args) > 1:
        for key in args[1].split('.'):
            data = data[key]
    if isinstance(data, dict):
        data = dict(data.items())
    pprint(data)


if __name__ == '__main__':
    main()
