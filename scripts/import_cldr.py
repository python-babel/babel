#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2007 Edgewall Software
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution. The terms
# are also available at http://babel.edgewall.org/wiki/License.
#
# This software consists of voluntary contributions made by many
# individuals. For the exact contribution history, see the revision
# history and logs, available at http://babel.edgewall.org/log/.

import copy
from optparse import OptionParser
import os
import pickle
import sys
try:
    from xml.etree.ElementTree import parse
except ImportError:
    from elementtree.ElementTree import parse

from babel import dates, numbers

weekdays = {'mon': 1, 'tue': 2, 'wed': 3, 'thu': 4, 'fri': 5, 'sat': 6,
            'sun': 7}

try:
    any
except NameError:
    def any(iterable):
        return filter(None, list(iterable))

def _parent(locale):
    parts = locale.split('_')
    if len(parts) == 1:
        return 'root'
    else:
        return '_'.join(parts[:-1])

def _text(elem):
    buf = [elem.text or '']
    for child in elem:
        buf.append(_text(child))
    buf.append(elem.tail or '')
    return u''.join(filter(None, buf)).strip()

def main():
    parser = OptionParser(usage='%prog path/to/cldr')
    options, args = parser.parse_args()
    if len(args) != 1:
        parser.error('incorrect number of arguments')

    srcdir = args[0]
    destdir = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])),
                           '..', 'babel', 'localedata')

    sup = parse(os.path.join(srcdir, 'supplemental', 'supplementalData.xml'))

    # build a territory containment mapping for inheritance
    regions = {}
    for elem in sup.findall('//territoryContainment/group'):
        regions[elem.attrib['type']] = elem.attrib['contains'].split()
    from pprint import pprint

    # Resolve territory containment
    territory_containment = {}
    region_items = regions.items()
    region_items.sort()
    for group, territory_list in region_items:
        for territory in territory_list:
            containers = territory_containment.setdefault(territory, set([]))
            if group in territory_containment:
                containers |= territory_containment[group]
            containers.add(group)

    filenames = os.listdir(os.path.join(srcdir, 'main'))
    filenames.remove('root.xml')
    filenames.sort(lambda a,b: len(a)-len(b))
    filenames.insert(0, 'root.xml')

    dicts = {}

    for filename in filenames:
        print>>sys.stderr, 'Processing input file %r' % filename
        stem, ext = os.path.splitext(filename)
        if ext != '.xml':
            continue

        data = {}
        if stem != 'root':
            data.update(copy.deepcopy(dicts[_parent(stem)]))
        tree = parse(os.path.join(srcdir, 'main', filename))

        language = None
        elem = tree.find('//identity/language')
        if elem is not None:
            language = elem.attrib['type']
        print>>sys.stderr, '  Language:  %r' % language

        territory = None
        elem = tree.find('//identity/territory')
        if elem is not None:
            territory = elem.attrib['type']
        print>>sys.stderr, '  Territory: %r' % territory
        regions = territory_containment.get(territory, [])
        print>>sys.stderr, '  Regions:    %r' % regions

        # <localeDisplayNames>

        territories = data.setdefault('territories', {})
        for elem in tree.findall('//territories/territory'):
            if 'draft' in elem.attrib and elem.attrib['type'] in territories:
                continue
            territories[elem.attrib['type']] = _text(elem)

        languages = data.setdefault('languages', {})
        for elem in tree.findall('//languages/language'):
            if 'draft' in elem.attrib and elem.attrib['type'] in languages:
                continue
            languages[elem.attrib['type']] = _text(elem)

        variants = data.setdefault('variants', {})
        for elem in tree.findall('//variants/variant'):
            if 'draft' in elem.attrib and elem.attrib['type'] in variants:
                continue
            variants[elem.attrib['type']] = _text(elem)

        scripts = data.setdefault('scripts', {})
        for elem in tree.findall('//scripts/script'):
            if 'draft' in elem.attrib and elem.attrib['type'] in scripts:
                continue
            scripts[elem.attrib['type']] = _text(elem)

        # <dates>

        week_data = data.setdefault('week_data', {})
        supelem = sup.find('//weekData')

        for elem in supelem.findall('minDays'):
            territories = elem.attrib['territories'].split()
            if territory in territories or any([r in territories for r in regions]):
                week_data['min_days'] = int(elem.attrib['count'])

        for elem in supelem.findall('firstDay'):
            territories = elem.attrib['territories'].split()
            if territory in territories or any([r in territories for r in regions]):
                week_data['first_day'] = weekdays[elem.attrib['day']]

        for elem in supelem.findall('weekendStart'):
            territories = elem.attrib['territories'].split()
            if territory in territories or any([r in territories for r in regions]):
                week_data['weekend_start'] = weekdays[elem.attrib['day']]

        for elem in supelem.findall('weekendEnd'):
            territories = elem.attrib['territories'].split()
            if territory in territories or any([r in territories for r in regions]):
                week_data['weekend_end'] = weekdays[elem.attrib['day']]

        time_zones = data.setdefault('time_zones', {})
        for elem in tree.findall('//timeZoneNames/zone'):
            time_zones[elem.tag] = unicode(elem.findtext('displayName'))

        for calendar in tree.findall('//calendars/calendar'):
            if calendar.attrib['type'] != 'gregorian':
                # TODO: support other calendar types
                continue

            months = data.setdefault('months', {})
            for ctxt in calendar.findall('months/monthContext'):
                ctxts = months.setdefault(ctxt.attrib['type'], {})
                for width in ctxt.findall('monthWidth'):
                    widths = ctxts.setdefault(width.attrib['type'], {})
                    for elem in width.findall('month'):
                        if 'draft' in elem.attrib and int(elem.attrib['type']) in widths:
                            continue
                        widths[int(elem.attrib.get('type'))] = unicode(elem.text)

            days = data.setdefault('days', {})
            for ctxt in calendar.findall('days/dayContext'):
                ctxts = days.setdefault(ctxt.attrib['type'], {})
                for width in ctxt.findall('dayWidth'):
                    widths = ctxts.setdefault(width.attrib['type'], {})
                    for elem in width.findall('day'):
                        dtype = weekdays[elem.attrib['type']]
                        if 'draft' in elem.attrib and dtype in widths:
                            continue
                        widths[dtype] = unicode(elem.text)

            quarters = data.setdefault('quarters', {})
            for ctxt in calendar.findall('quarters/quarterContext'):
                ctxts = quarters.setdefault(ctxt.attrib['type'], {})
                for width in ctxt.findall('quarterWidth'):
                    widths = ctxts.setdefault(width.attrib['type'], {})
                    for elem in width.findall('quarter'):
                        if 'draft' in elem.attrib and int(elem.attrib['type']) in widths:
                            continue
                        widths[int(elem.attrib.get('type'))] = unicode(elem.text)

            eras = data.setdefault('eras', {})
            for width in calendar.findall('eras/*'):
                ewidth = {'eraNames': 'wide', 'eraAbbr': 'abbreviated'}[width.tag]
                widths = eras.setdefault(ewidth, {})
                for elem in width.findall('era'):
                    if 'draft' in elem.attrib and int(elem.attrib['type']) in widths:
                        continue
                    widths[int(elem.attrib.get('type'))] = unicode(elem.text)

            # AM/PM
            periods = data.setdefault('periods', {})
            for elem in calendar.findall('am'):
                if 'draft' in elem.attrib and elem.tag in periods:
                    continue
                periods[elem.tag] = unicode(elem.text)
            for elem in calendar.findall('pm'):
                if 'draft' in elem.attrib and elem.tag in periods:
                    continue
                periods[elem.tag] = unicode(elem.text)

            date_formats = data.setdefault('date_formats', {})
            for elem in calendar.findall('dateFormats/dateFormatLength'):
                if 'draft' in elem.attrib and elem.attrib.get('type') in date_formats:
                    continue
                try:
                    date_formats[elem.attrib.get('type')] = \
                        dates.parse_pattern(unicode(elem.findtext('dateFormat/pattern')))
                except ValueError, e:
                    print e

            time_formats = data.setdefault('time_formats', {})
            for elem in calendar.findall('timeFormats/timeFormatLength'):
                if 'draft' in elem.attrib and elem.attrib.get('type') in time_formats:
                    continue
                try:
                    time_formats[elem.attrib.get('type')] = \
                        dates.parse_pattern(unicode(elem.findtext('timeFormat/pattern')))
                except ValueError, e:
                    print e

        # <numbers>

        number_symbols = data.setdefault('number_symbols', {})
        for elem in tree.findall('//numbers/symbols/*'):
            number_symbols[elem.tag] = unicode(elem.text)

        decimal_formats = data.setdefault('decimal_formats', {})
        for elem in tree.findall('//decimalFormats/decimalFormatLength'):
            if 'draft' in elem.attrib and elem.attrib.get('type') in decimal_formats:
                continue
            decimal_formats[elem.attrib.get('type')] = numbers.parse_pattern(unicode(elem.findtext('decimalFormat/pattern')))

        scientific_formats = data.setdefault('scientific_formats', {})
        for elem in tree.findall('//scientificFormats/scientificFormatLength'):
            if 'draft' in elem.attrib and elem.attrib.get('type') in scientific_formats:
                continue
            scientific_formats[elem.attrib.get('type')] = unicode(elem.findtext('scientificFormat/pattern'))

        currency_formats = data.setdefault('currency_formats', {})
        for elem in tree.findall('//currencyFormats/currencyFormatLength'):
            if 'draft' in elem.attrib and elem.attrib.get('type') in currency_formats:
                continue
            currency_formats[elem.attrib.get('type')] = unicode(elem.findtext('currencyFormat/pattern'))

        percent_formats = data.setdefault('percent_formats', {})
        for elem in tree.findall('//percentFormats/percentFormatLength'):
            if 'draft' in elem.attrib and elem.attrib.get('type') in percent_formats:
                continue
            percent_formats[elem.attrib.get('type')] = unicode(elem.findtext('percentFormat/pattern'))

        currencies = data.setdefault('currencies', {})
        for elem in tree.findall('//currencies/currency'):
            currencies[elem.attrib['type']] = {
                'display_name': unicode(elem.findtext('displayName')),
                'symbol': unicode(elem.findtext('symbol'))
            }

        dicts[stem] = data
        outfile = open(os.path.join(destdir, stem + '.dat'), 'wb')
        try:
            pickle.dump(data, outfile, 2)
        finally:
            outfile.close()

if __name__ == '__main__':
    main()
