#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2007-2011 Edgewall Software
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution. The terms
# are also available at http://babel.edgewall.org/wiki/License.
#
# This software consists of voluntary contributions made by many
# individuals. For the exact contribution history, see the revision
# history and logs, available at http://babel.edgewall.org/log/.

from optparse import OptionParser
import os
import re
import sys
try:
    from xml.etree import cElementTree as ElementTree
except ImportError:
    from xml.etree import ElementTree

from datetime import date

# Make sure we're using Babel source, and not some previously installed version
sys.path.insert(0, os.path.join(os.path.dirname(sys.argv[0]), '..'))

from babel import dates, numbers
from babel.plural import PluralRule
from babel.localedata import Alias
from babel._compat import pickle, text_type

parse = ElementTree.parse
weekdays = {'mon': 0, 'tue': 1, 'wed': 2, 'thu': 3, 'fri': 4, 'sat': 5,
            'sun': 6}


def _text(elem):
    buf = [elem.text or '']
    for child in elem:
        buf.append(_text(child))
    buf.append(elem.tail or '')
    return u''.join(filter(None, buf)).strip()


NAME_RE = re.compile(r"^\w+$")
TYPE_ATTR_RE = re.compile(r"^\w+\[@type='(.*?)'\]$")

NAME_MAP = {
    'dateFormats': 'date_formats',
    'dateTimeFormats': 'datetime_formats',
    'eraAbbr': 'abbreviated',
    'eraNames': 'wide',
    'eraNarrow': 'narrow',
    'timeFormats': 'time_formats'
}


def log(message, *args):
    if args:
        message = message % args
    sys.stderr.write(message + '\r\n')
    sys.stderr.flush()


def error(message, *args):
    log('ERROR: %s' % message, *args)


def need_conversion(dst_filename, data_dict, source_filename):
    with open(source_filename, 'rb') as f:
        blob = f.read(4096)
        version = int(re.search(b'version number="\\$Revision: (\\d+)',
                                blob).group(1))

    data_dict['_version'] = version
    if not os.path.isfile(dst_filename):
        return True

    with open(dst_filename, 'rb') as f:
        data = pickle.load(f)
        return data.get('_version') != version


def _translate_alias(ctxt, path):
    parts = path.split('/')
    keys = ctxt[:]
    for part in parts:
        if part == '..':
            keys.pop()
        else:
            match = TYPE_ATTR_RE.match(part)
            if match:
                keys.append(match.group(1))
            else:
                assert NAME_RE.match(part)
                keys.append(NAME_MAP.get(part, part))
    return keys


def _parse_currency_date(s):
    if not s:
        return None
    parts = s.split('-', 2)
    return date(*map(int, parts + [1] * (3 - len(parts))))


def _currency_sort_key(tup):
    code, start, end, tender = tup
    return int(not tender), start or date(1, 1, 1)


def main():
    parser = OptionParser(usage='%prog path/to/cldr')
    options, args = parser.parse_args()
    if len(args) != 1:
        parser.error('incorrect number of arguments')

    srcdir = args[0]
    destdir = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])),
                           '..', 'babel')

    sup_filename = os.path.join(srcdir, 'supplemental', 'supplementalData.xml')
    bcp47_timezone = parse(os.path.join(srcdir, 'bcp47', 'timezone.xml'))
    sup_windows_zones = parse(os.path.join(srcdir, 'supplemental',
                                           'windowsZones.xml'))
    sup_metadata = parse(os.path.join(srcdir, 'supplemental',
                                      'supplementalMetadata.xml'))
    sup_likely = parse(os.path.join(srcdir, 'supplemental',
                                    'likelySubtags.xml'))
    sup = parse(sup_filename)

    # Import global data from the supplemental files
    global_path = os.path.join(destdir, 'global.dat')
    global_data = {}
    if need_conversion(global_path, global_data, sup_filename):
        territory_zones = global_data.setdefault('territory_zones', {})
        zone_aliases = global_data.setdefault('zone_aliases', {})
        zone_territories = global_data.setdefault('zone_territories', {})
        win_mapping = global_data.setdefault('windows_zone_mapping', {})
        language_aliases = global_data.setdefault('language_aliases', {})
        territory_aliases = global_data.setdefault('territory_aliases', {})
        script_aliases = global_data.setdefault('script_aliases', {})
        variant_aliases = global_data.setdefault('variant_aliases', {})
        likely_subtags = global_data.setdefault('likely_subtags', {})
        territory_currencies = global_data.setdefault('territory_currencies', {})
        parent_exceptions = global_data.setdefault('parent_exceptions', {})

        # create auxiliary zone->territory map from the windows zones (we don't set
        # the 'zones_territories' map directly here, because there are some zones
        # aliases listed and we defer the decision of which ones to choose to the
        # 'bcp47' data
        _zone_territory_map = {}
        for map_zone in sup_windows_zones.findall(
                './/windowsZones/mapTimezones/mapZone'):
            if map_zone.attrib.get('territory') == '001':
                win_mapping[map_zone.attrib['other']] = \
                    map_zone.attrib['type'].split()[0]
            for tzid in text_type(map_zone.attrib['type']).split():
                _zone_territory_map[tzid] = \
                    text_type(map_zone.attrib['territory'])

        for key_elem in bcp47_timezone.findall('.//keyword/key'):
            if key_elem.attrib['name'] == 'tz':
                for elem in key_elem.findall('type'):
                    aliases = text_type(elem.attrib['alias']).split()
                    tzid = aliases.pop(0)
                    territory = _zone_territory_map.get(tzid, '001')
                    territory_zones.setdefault(territory, []).append(tzid)
                    zone_territories[tzid] = territory
                    for alias in aliases:
                        zone_aliases[alias] = tzid
                break

        # Import Metazone mapping
        meta_zones = global_data.setdefault('meta_zones', {})
        tzsup = parse(os.path.join(srcdir, 'supplemental', 'metaZones.xml'))
        for elem in tzsup.findall('.//timezone'):
            for child in elem.findall('usesMetazone'):
                if 'to' not in child.attrib: # FIXME: support old mappings
                    meta_zones[elem.attrib['type']] = child.attrib['mzone']

        # Language aliases
        for alias in sup_metadata.findall('.//alias/languageAlias'):
            # We don't have a use for those at the moment.  They don't
            # pass our parser anyways.
            if '-' in alias.attrib['type']:
                continue
            language_aliases[alias.attrib['type']] = alias.attrib['replacement']

        # Territory aliases
        for alias in sup_metadata.findall('.//alias/territoryAlias'):
            territory_aliases[alias.attrib['type']] = \
                alias.attrib['replacement'].split()

        # Script aliases
        for alias in sup_metadata.findall('.//alias/scriptAlias'):
            script_aliases[alias.attrib['type']] = alias.attrib['replacement']

        # Variant aliases
        for alias in sup_metadata.findall('.//alias/variantAlias'):
            repl = alias.attrib.get('replacement')
            if repl:
                variant_aliases[alias.attrib['type']] = repl

        # Likely subtags
        for likely_subtag in sup_likely.findall('.//likelySubtags/likelySubtag'):
            likely_subtags[likely_subtag.attrib['from']] = \
                likely_subtag.attrib['to']

        # Currencies in territories
        for region in sup.findall('.//currencyData/region'):
            region_code = region.attrib['iso3166']
            region_currencies = []
            for currency in region.findall('./currency'):
                cur_start = _parse_currency_date(currency.attrib.get('from'))
                cur_end = _parse_currency_date(currency.attrib.get('to'))
                region_currencies.append((currency.attrib['iso4217'],
                                          cur_start, cur_end,
                                          currency.attrib.get(
                                              'tender', 'true') == 'true'))
            region_currencies.sort(key=_currency_sort_key)
            territory_currencies[region_code] = region_currencies

        # Explicit parent locales
        for paternity in sup.findall('.//parentLocales/parentLocale'):
            parent = paternity.attrib['parent']
            for child in paternity.attrib['locales'].split():
                parent_exceptions[child] = parent

        outfile = open(global_path, 'wb')
        try:
            pickle.dump(global_data, outfile, 2)
        finally:
            outfile.close()

    # build a territory containment mapping for inheritance
    regions = {}
    for elem in sup.findall('.//territoryContainment/group'):
        regions[elem.attrib['type']] = elem.attrib['contains'].split()

    # Resolve territory containment
    territory_containment = {}
    region_items = sorted(regions.items())
    for group, territory_list in region_items:
        for territory in territory_list:
            containers = territory_containment.setdefault(territory, set([]))
            if group in territory_containment:
                containers |= territory_containment[group]
            containers.add(group)

    # prepare the per-locale plural rules definitions
    plural_rules = {}
    prsup = parse(os.path.join(srcdir, 'supplemental', 'plurals.xml'))
    for elem in prsup.findall('.//plurals/pluralRules'):
        rules = []
        for rule in elem.findall('pluralRule'):
            rules.append((rule.attrib['count'], text_type(rule.text)))
        pr = PluralRule(rules)
        for locale in elem.attrib['locales'].split():
            plural_rules[locale] = pr

    filenames = os.listdir(os.path.join(srcdir, 'main'))
    filenames.remove('root.xml')
    filenames.sort(key=len)
    filenames.insert(0, 'root.xml')

    for filename in filenames:
        stem, ext = os.path.splitext(filename)
        if ext != '.xml':
            continue

        full_filename = os.path.join(srcdir, 'main', filename)
        data_filename = os.path.join(destdir, 'localedata', stem + '.dat')

        data = {}
        if not need_conversion(data_filename, data, full_filename):
            continue

        tree = parse(full_filename)

        language = None
        elem = tree.find('.//identity/language')
        if elem is not None:
            language = elem.attrib['type']

        territory = None
        elem = tree.find('.//identity/territory')
        if elem is not None:
            territory = elem.attrib['type']
        else:
            territory = '001' # world
        regions = territory_containment.get(territory, [])

        log('Processing %s (Language = %s; Territory = %s)',
            filename, language, territory)

        # plural rules
        locale_id = '_'.join(filter(None, [
            language,
            territory != '001' and territory or None
        ]))
        if locale_id in plural_rules:
            data['plural_form'] = plural_rules[locale_id]

        # <localeDisplayNames>

        territories = data.setdefault('territories', {})
        for elem in tree.findall('.//territories/territory'):
            if ('draft' in elem.attrib or 'alt' in elem.attrib) \
                    and elem.attrib['type'] in territories:
                continue
            territories[elem.attrib['type']] = _text(elem)

        languages = data.setdefault('languages', {})
        for elem in tree.findall('.//languages/language'):
            if ('draft' in elem.attrib or 'alt' in elem.attrib) \
                    and elem.attrib['type'] in languages:
                continue
            languages[elem.attrib['type']] = _text(elem)

        variants = data.setdefault('variants', {})
        for elem in tree.findall('.//variants/variant'):
            if ('draft' in elem.attrib or 'alt' in elem.attrib) \
                    and elem.attrib['type'] in variants:
                continue
            variants[elem.attrib['type']] = _text(elem)

        scripts = data.setdefault('scripts', {})
        for elem in tree.findall('.//scripts/script'):
            if ('draft' in elem.attrib or 'alt' in elem.attrib) \
                    and elem.attrib['type'] in scripts:
                continue
            scripts[elem.attrib['type']] = _text(elem)

        # <dates>

        week_data = data.setdefault('week_data', {})
        supelem = sup.find('.//weekData')

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

        zone_formats = data.setdefault('zone_formats', {})
        for elem in tree.findall('.//timeZoneNames/gmtFormat'):
            if 'draft' not in elem.attrib and 'alt' not in elem.attrib:
                zone_formats['gmt'] = text_type(elem.text).replace('{0}', '%s')
                break
        for elem in tree.findall('.//timeZoneNames/regionFormat'):
            if 'draft' not in elem.attrib and 'alt' not in elem.attrib:
                zone_formats['region'] = text_type(elem.text).replace('{0}', '%s')
                break
        for elem in tree.findall('.//timeZoneNames/fallbackFormat'):
            if 'draft' not in elem.attrib and 'alt' not in elem.attrib:
                zone_formats['fallback'] = text_type(elem.text) \
                    .replace('{0}', '%(0)s').replace('{1}', '%(1)s')
                break
        for elem in tree.findall('.//timeZoneNames/fallbackRegionFormat'):
            if 'draft' not in elem.attrib and 'alt' not in elem.attrib:
                zone_formats['fallback_region'] = text_type(elem.text) \
                    .replace('{0}', '%(0)s').replace('{1}', '%(1)s')
                break

        time_zones = data.setdefault('time_zones', {})
        for elem in tree.findall('.//timeZoneNames/zone'):
            info = {}
            city = elem.findtext('exemplarCity')
            if city:
                info['city'] = text_type(city)
            for child in elem.findall('long/*'):
                info.setdefault('long', {})[child.tag] = text_type(child.text)
            for child in elem.findall('short/*'):
                info.setdefault('short', {})[child.tag] = text_type(child.text)
            time_zones[elem.attrib['type']] = info

        meta_zones = data.setdefault('meta_zones', {})
        for elem in tree.findall('.//timeZoneNames/metazone'):
            info = {}
            city = elem.findtext('exemplarCity')
            if city:
                info['city'] = text_type(city)
            for child in elem.findall('long/*'):
                info.setdefault('long', {})[child.tag] = text_type(child.text)
            for child in elem.findall('short/*'):
                info.setdefault('short', {})[child.tag] = text_type(child.text)
            meta_zones[elem.attrib['type']] = info

        for calendar in tree.findall('.//calendars/calendar'):
            if calendar.attrib['type'] != 'gregorian':
                # TODO: support other calendar types
                continue

            months = data.setdefault('months', {})
            for ctxt in calendar.findall('months/monthContext'):
                ctxt_type = ctxt.attrib['type']
                ctxts = months.setdefault(ctxt_type, {})
                for width in ctxt.findall('monthWidth'):
                    width_type = width.attrib['type']
                    widths = ctxts.setdefault(width_type, {})
                    for elem in width.getiterator():
                        if elem.tag == 'month':
                            if ('draft' in elem.attrib or 'alt' in elem.attrib) \
                                    and int(elem.attrib['type']) in widths:
                                continue
                            widths[int(elem.attrib.get('type'))] = \
                                text_type(elem.text)
                        elif elem.tag == 'alias':
                            ctxts[width_type] = Alias(
                                _translate_alias(['months', ctxt_type, width_type],
                                                 elem.attrib['path'])
                            )

            days = data.setdefault('days', {})
            for ctxt in calendar.findall('days/dayContext'):
                ctxt_type = ctxt.attrib['type']
                ctxts = days.setdefault(ctxt_type, {})
                for width in ctxt.findall('dayWidth'):
                    width_type = width.attrib['type']
                    widths = ctxts.setdefault(width_type, {})
                    for elem in width.getiterator():
                        if elem.tag == 'day':
                            dtype = weekdays[elem.attrib['type']]
                            if ('draft' in elem.attrib or
                                'alt' not in elem.attrib) \
                                    and dtype in widths:
                                continue
                            widths[dtype] = text_type(elem.text)
                        elif elem.tag == 'alias':
                            ctxts[width_type] = Alias(
                                _translate_alias(['days', ctxt_type, width_type],
                                                 elem.attrib['path'])
                            )

            quarters = data.setdefault('quarters', {})
            for ctxt in calendar.findall('quarters/quarterContext'):
                ctxt_type = ctxt.attrib['type']
                ctxts = quarters.setdefault(ctxt.attrib['type'], {})
                for width in ctxt.findall('quarterWidth'):
                    width_type = width.attrib['type']
                    widths = ctxts.setdefault(width_type, {})
                    for elem in width.getiterator():
                        if elem.tag == 'quarter':
                            if ('draft' in elem.attrib or 'alt' in elem.attrib) \
                                    and int(elem.attrib['type']) in widths:
                                continue
                            widths[int(elem.attrib['type'])] = text_type(elem.text)
                        elif elem.tag == 'alias':
                            ctxts[width_type] = Alias(
                                _translate_alias(['quarters', ctxt_type,
                                                  width_type],
                                                 elem.attrib['path']))

            eras = data.setdefault('eras', {})
            for width in calendar.findall('eras/*'):
                width_type = NAME_MAP[width.tag]
                widths = eras.setdefault(width_type, {})
                for elem in width.getiterator():
                    if elem.tag == 'era':
                        if ('draft' in elem.attrib or 'alt' in elem.attrib) \
                                and int(elem.attrib['type']) in widths:
                            continue
                        widths[int(elem.attrib.get('type'))] = text_type(elem.text)
                    elif elem.tag == 'alias':
                        eras[width_type] = Alias(
                            _translate_alias(['eras', width_type],
                                             elem.attrib['path'])
                        )

            # AM/PM
            periods = data.setdefault('periods', {})
            for day_period_width in calendar.findall(
                    'dayPeriods/dayPeriodContext/dayPeriodWidth'):
                if day_period_width.attrib['type'] == 'wide':
                    for day_period in day_period_width.findall('dayPeriod'):
                        if 'alt' not in day_period.attrib:
                            periods[day_period.attrib['type']] = text_type(
                                day_period.text)

            date_formats = data.setdefault('date_formats', {})
            for format in calendar.findall('dateFormats'):
                for elem in format.getiterator():
                    if elem.tag == 'dateFormatLength':
                        if 'draft' in elem.attrib and \
                                elem.attrib.get('type') in date_formats:
                            continue
                        try:
                            date_formats[elem.attrib.get('type')] = \
                                dates.parse_pattern(text_type(
                                    elem.findtext('dateFormat/pattern')))
                        except ValueError as e:
                            error(e)
                    elif elem.tag == 'alias':
                        date_formats = Alias(_translate_alias(
                            ['date_formats'], elem.attrib['path'])
                        )

            time_formats = data.setdefault('time_formats', {})
            for format in calendar.findall('timeFormats'):
                for elem in format.getiterator():
                    if elem.tag == 'timeFormatLength':
                        if ('draft' in elem.attrib or 'alt' in elem.attrib) \
                                and elem.attrib.get('type') in time_formats:
                            continue
                        try:
                            time_formats[elem.attrib.get('type')] = \
                                dates.parse_pattern(text_type(
                                    elem.findtext('timeFormat/pattern')))
                        except ValueError as e:
                            error(e)
                    elif elem.tag == 'alias':
                        time_formats = Alias(_translate_alias(
                            ['time_formats'], elem.attrib['path'])
                        )

            datetime_formats = data.setdefault('datetime_formats', {})
            for format in calendar.findall('dateTimeFormats'):
                for elem in format.getiterator():
                    if elem.tag == 'dateTimeFormatLength':
                        if ('draft' in elem.attrib or 'alt' in elem.attrib) \
                                and elem.attrib.get('type') in datetime_formats:
                            continue
                        try:
                            datetime_formats[elem.attrib.get('type')] = \
                                text_type(elem.findtext('dateTimeFormat/pattern'))
                        except ValueError as e:
                            error(e)
                    elif elem.tag == 'alias':
                        datetime_formats = Alias(_translate_alias(
                            ['datetime_formats'], elem.attrib['path'])
                        )

        # <numbers>

        number_symbols = data.setdefault('number_symbols', {})
        for elem in tree.findall('.//numbers/symbols/*'):
            if ('draft' in elem.attrib or 'alt' in elem.attrib):
                continue
            number_symbols[elem.tag] = text_type(elem.text)

        decimal_formats = data.setdefault('decimal_formats', {})
        for elem in tree.findall('.//decimalFormats/decimalFormatLength'):
            if ('draft' in elem.attrib or 'alt' in elem.attrib) \
                    and elem.attrib.get('type') in decimal_formats:
                continue
            if elem.findall('./alias'):
                # TODO map the alias to its target
                continue
            pattern = text_type(elem.findtext('./decimalFormat/pattern'))
            decimal_formats[elem.attrib.get('type')] = \
                numbers.parse_pattern(pattern)

        scientific_formats = data.setdefault('scientific_formats', {})
        for elem in tree.findall('.//scientificFormats/scientificFormatLength'):
            if ('draft' in elem.attrib or 'alt' in elem.attrib) \
                    and elem.attrib.get('type') in scientific_formats:
                continue
            pattern = text_type(elem.findtext('scientificFormat/pattern'))
            scientific_formats[elem.attrib.get('type')] = \
                numbers.parse_pattern(pattern)

        currency_formats = data.setdefault('currency_formats', {})
        for elem in tree.findall('.//currencyFormats/currencyFormatLength'):
            if ('draft' in elem.attrib or 'alt' in elem.attrib) \
                    and elem.attrib.get('type') in currency_formats:
                continue
            pattern = text_type(elem.findtext('currencyFormat/pattern'))
            currency_formats[elem.attrib.get('type')] = \
                numbers.parse_pattern(pattern)

        percent_formats = data.setdefault('percent_formats', {})
        for elem in tree.findall('.//percentFormats/percentFormatLength'):
            if ('draft' in elem.attrib or 'alt' in elem.attrib) \
                    and elem.attrib.get('type') in percent_formats:
                continue
            pattern = text_type(elem.findtext('percentFormat/pattern'))
            percent_formats[elem.attrib.get('type')] = \
                numbers.parse_pattern(pattern)

        currency_names = data.setdefault('currency_names', {})
        currency_names_plural = data.setdefault('currency_names_plural', {})
        currency_symbols = data.setdefault('currency_symbols', {})
        for elem in tree.findall('.//currencies/currency'):
            code = elem.attrib['type']
            for name in elem.findall('displayName'):
                if ('draft' in name.attrib) and code in currency_names:
                    continue
                if 'count' in name.attrib:
                    currency_names_plural.setdefault(code, {})[
                        name.attrib['count']] = text_type(name.text)
                else:
                    currency_names[code] = text_type(name.text)
            # TODO: support choice patterns for currency symbol selection
            symbol = elem.find('symbol')
            if symbol is not None and 'draft' not in symbol.attrib \
                    and 'choice' not in symbol.attrib:
                currency_symbols[code] = text_type(symbol.text)

        # <units>

        unit_patterns = data.setdefault('unit_patterns', {})
        for elem in tree.findall('.//units/unit'):
            unit_type = elem.attrib['type']
            for pattern in elem.findall('unitPattern'):
                box = unit_type
                if 'alt' in pattern.attrib:
                    box += ':' + pattern.attrib['alt']
                unit_patterns.setdefault(box, {})[pattern.attrib['count']] = \
                    text_type(pattern.text)

        outfile = open(data_filename, 'wb')
        try:
            pickle.dump(data, outfile, 2)
        finally:
            outfile.close()


if __name__ == '__main__':
    main()
