#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2007-2011 Edgewall Software, 2013-2020 the Babel team
# All rights reserved.
#
# This software is licensed as described in the file LICENSE, which
# you should have received as part of this distribution. The terms
# are also available at http://babel.edgewall.org/wiki/License.
#
# This software consists of voluntary contributions made by many
# individuals. For the exact contribution history, see the revision
# history and logs, available at http://babel.edgewall.org/log/.

import collections
from optparse import OptionParser
import os
import re
import sys
import logging

try:
    from xml.etree import cElementTree as ElementTree
except ImportError:
    from xml.etree import ElementTree

# Make sure we're using Babel source, and not some previously installed version
CHECKOUT_ROOT = os.path.abspath(os.path.join(
    os.path.dirname(__file__),
    '..'
))
BABEL_PACKAGE_ROOT = os.path.join(CHECKOUT_ROOT, "babel")
sys.path.insert(0, CHECKOUT_ROOT)

from babel import dates, numbers
from babel._compat import pickle, text_type
from babel.dates import split_interval_pattern
from babel.localedata import Alias
from babel.plural import PluralRule

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

log = logging.getLogger("import_cldr")


def need_conversion(dst_filename, data_dict, source_filename):
    with open(source_filename, 'rb') as f:
        blob = f.read(4096)
        version_match = re.search(b'version number="\\$Revision: (\\d+)', blob)
        if not version_match:  # CLDR 36.0 was shipped without proper revision numbers
            return True
        version = int(version_match.group(1))

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
    return tuple(map(int, parts + [1] * (3 - len(parts))))


def _currency_sort_key(tup):
    code, start, end, tender = tup
    return int(not tender), start or (1, 1, 1)


def _extract_plural_rules(file_path):
    rule_dict = {}
    prsup = parse(file_path)
    for elem in prsup.findall('.//plurals/pluralRules'):
        rules = []
        for rule in elem.findall('pluralRule'):
            rules.append((rule.attrib['count'], text_type(rule.text)))
        pr = PluralRule(rules)
        for locale in elem.attrib['locales'].split():
            rule_dict[locale] = pr
    return rule_dict


def _time_to_seconds_past_midnight(time_expr):
    """
    Parse a time expression to seconds after midnight.
    :param time_expr: Time expression string (H:M or H:M:S)
    :rtype: int
    """
    if time_expr is None:
        return None
    if time_expr.count(":") == 1:
        time_expr += ":00"
    hour, minute, second = [int(p, 10) for p in time_expr.split(":")]
    return hour * 60 * 60 + minute * 60 + second


def _compact_dict(dict):
    """
    "Compact" the given dict by removing items whose value is None or False.
    """
    out_dict = {}
    for key, value in dict.items():
        if value is not None and value is not False:
            out_dict[key] = value
    return out_dict


def debug_repr(obj):
    if isinstance(obj, PluralRule):
        return obj.abstract
    return repr(obj)


def write_datafile(path, data, dump_json=False):
    with open(path, 'wb') as outfile:
        pickle.dump(data, outfile, 2)
    if dump_json:
        import json
        with open(path + '.json', 'w') as outfile:
            json.dump(data, outfile, indent=4, default=debug_repr)


def main():
    parser = OptionParser(usage='%prog path/to/cldr')
    parser.add_option(
        '-f', '--force', dest='force', action='store_true', default=False,
        help='force import even if destination file seems up to date'
    )
    parser.add_option(
        '-j', '--json', dest='dump_json', action='store_true', default=False,
        help='also export debugging JSON dumps of locale data'
    )
    parser.add_option(
        '-q', '--quiet', dest='quiet', action='store_true', default=bool(os.environ.get('BABEL_CLDR_QUIET')),
        help='quiesce info/warning messages',
    )

    options, args = parser.parse_args()
    if len(args) != 1:
        parser.error('incorrect number of arguments')

    logging.basicConfig(
        level=(logging.ERROR if options.quiet else logging.INFO),
    )

    return process_data(
        srcdir=args[0],
        destdir=BABEL_PACKAGE_ROOT,
        force=bool(options.force),
        dump_json=bool(options.dump_json)
    )


def process_data(srcdir, destdir, force=False, dump_json=False):
    sup_filename = os.path.join(srcdir, 'supplemental', 'supplementalData.xml')
    sup = parse(sup_filename)

    # Import global data from the supplemental files
    global_path = os.path.join(destdir, 'global.dat')
    global_data = {}
    if force or need_conversion(global_path, global_data, sup_filename):
        global_data.update(parse_global(srcdir, sup))
        write_datafile(global_path, global_data, dump_json=dump_json)
    _process_local_datas(sup, srcdir, destdir, force=force, dump_json=dump_json)


def parse_global(srcdir, sup):
    global_data = {}
    sup_dir = os.path.join(srcdir, 'supplemental')
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
    all_currencies = collections.defaultdict(set)
    currency_fractions = global_data.setdefault('currency_fractions', {})
    territory_languages = global_data.setdefault('territory_languages', {})
    bcp47_timezone = parse(os.path.join(srcdir, 'bcp47', 'timezone.xml'))
    sup_windows_zones = parse(os.path.join(sup_dir, 'windowsZones.xml'))
    sup_metadata = parse(os.path.join(sup_dir, 'supplementalMetadata.xml'))
    sup_likely = parse(os.path.join(sup_dir, 'likelySubtags.xml'))
    # create auxiliary zone->territory map from the windows zones (we don't set
    # the 'zones_territories' map directly here, because there are some zones
    # aliases listed and we defer the decision of which ones to choose to the
    # 'bcp47' data
    _zone_territory_map = {}
    for map_zone in sup_windows_zones.findall('.//windowsZones/mapTimezones/mapZone'):
        if map_zone.attrib.get('territory') == '001':
            win_mapping[map_zone.attrib['other']] = map_zone.attrib['type'].split()[0]
        for tzid in text_type(map_zone.attrib['type']).split():
            _zone_territory_map[tzid] = text_type(map_zone.attrib['territory'])
    for key_elem in bcp47_timezone.findall('.//keyword/key'):
        if key_elem.attrib['name'] == 'tz':
            for elem in key_elem.findall('type'):
                if 'deprecated' not in elem.attrib:
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
            if 'to' not in child.attrib:  # FIXME: support old mappings
                meta_zones[elem.attrib['type']] = child.attrib['mzone']

    # Language aliases
    for alias in sup_metadata.findall('.//alias/languageAlias'):
        # We don't have a use for those at the moment.  They don't
        # pass our parser anyways.
        if '_' in alias.attrib['type']:
            continue
        language_aliases[alias.attrib['type']] = alias.attrib['replacement']

    # Territory aliases
    for alias in sup_metadata.findall('.//alias/territoryAlias'):
        territory_aliases[alias.attrib['type']] = alias.attrib['replacement'].split()

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
        likely_subtags[likely_subtag.attrib['from']] = likely_subtag.attrib['to']

    # Currencies in territories
    for region in sup.findall('.//currencyData/region'):
        region_code = region.attrib['iso3166']
        region_currencies = []
        for currency in region.findall('./currency'):
            cur_code = currency.attrib['iso4217']
            cur_start = _parse_currency_date(currency.attrib.get('from'))
            cur_end = _parse_currency_date(currency.attrib.get('to'))
            cur_tender = currency.attrib.get('tender', 'true') == 'true'
            # Tie region to currency.
            region_currencies.append((cur_code, cur_start, cur_end, cur_tender))
            # Keep a reverse index of currencies to territorie.
            all_currencies[cur_code].add(region_code)
        region_currencies.sort(key=_currency_sort_key)
        territory_currencies[region_code] = region_currencies
    global_data['all_currencies'] = dict([
        (currency, tuple(sorted(regions))) for currency, regions in all_currencies.items()])

    # Explicit parent locales
    for paternity in sup.findall('.//parentLocales/parentLocale'):
        parent = paternity.attrib['parent']
        for child in paternity.attrib['locales'].split():
            parent_exceptions[child] = parent

    # Currency decimal and rounding digits
    for fraction in sup.findall('.//currencyData/fractions/info'):
        cur_code = fraction.attrib['iso4217']
        cur_digits = int(fraction.attrib['digits'])
        cur_rounding = int(fraction.attrib['rounding'])
        cur_cdigits = int(fraction.attrib.get('cashDigits', cur_digits))
        cur_crounding = int(fraction.attrib.get('cashRounding', cur_rounding))
        currency_fractions[cur_code] = (cur_digits, cur_rounding, cur_cdigits, cur_crounding)

    # Languages in territories
    for territory in sup.findall('.//territoryInfo/territory'):
        languages = {}
        for language in territory.findall('./languagePopulation'):
            languages[language.attrib['type']] = {
                'population_percent': float(language.attrib['populationPercent']),
                'official_status': language.attrib.get('officialStatus'),
            }
        territory_languages[territory.attrib['type']] = languages
    return global_data


def _process_local_datas(sup, srcdir, destdir, force=False, dump_json=False):
    day_period_rules = parse_day_period_rules(parse(os.path.join(srcdir, 'supplemental', 'dayPeriods.xml')))
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
    plural_rules = _extract_plural_rules(os.path.join(srcdir, 'supplemental', 'plurals.xml'))
    ordinal_rules = _extract_plural_rules(os.path.join(srcdir, 'supplemental', 'ordinals.xml'))

    filenames = os.listdir(os.path.join(srcdir, 'main'))
    filenames.remove('root.xml')
    filenames.sort(key=len)
    filenames.insert(0, 'root.xml')

    for filename in filenames:
        stem, ext = os.path.splitext(filename)
        if ext != '.xml':
            continue

        full_filename = os.path.join(srcdir, 'main', filename)
        data_filename = os.path.join(destdir, 'locale-data', stem + '.dat')

        data = {}
        if not (force or need_conversion(data_filename, data, full_filename)):
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
            territory = '001'  # world
        regions = territory_containment.get(territory, [])

        log.info(
            'Processing %s (Language = %s; Territory = %s)',
            filename, language, territory,
        )

        locale_id = '_'.join(filter(None, [
            language,
            territory != '001' and territory or None
        ]))

        data['locale_id'] = locale_id
        data['unsupported_number_systems'] = set()

        if locale_id in plural_rules:
            data['plural_form'] = plural_rules[locale_id]
        if locale_id in ordinal_rules:
            data['ordinal_form'] = ordinal_rules[locale_id]
        if locale_id in day_period_rules:
            data["day_period_rules"] = day_period_rules[locale_id]

        parse_locale_display_names(data, tree)
        parse_list_patterns(data, tree)
        parse_dates(data, tree, sup, regions, territory)

        for calendar in tree.findall('.//calendars/calendar'):
            if calendar.attrib['type'] != 'gregorian':
                # TODO: support other calendar types
                continue

            parse_calendar_months(data, calendar)
            parse_calendar_days(data, calendar)
            parse_calendar_quarters(data, calendar)
            parse_calendar_eras(data, calendar)
            parse_calendar_periods(data, calendar)
            parse_calendar_date_formats(data, calendar)
            parse_calendar_time_formats(data, calendar)
            parse_calendar_datetime_skeletons(data, calendar)
            parse_interval_formats(data, calendar)

        parse_number_symbols(data, tree)
        parse_decimal_formats(data, tree)
        parse_scientific_formats(data, tree)
        parse_percent_formats(data, tree)

        parse_currency_formats(data, tree)
        parse_currency_unit_patterns(data, tree)
        parse_currency_names(data, tree)
        parse_unit_patterns(data, tree)
        parse_date_fields(data, tree)
        parse_character_order(data, tree)
        parse_measurement_systems(data, tree)

        unsupported_number_systems_string = ', '.join(sorted(data.pop('unsupported_number_systems')))
        if unsupported_number_systems_string:
            log.warning('%s: unsupported number systems were ignored: %s' % (
                locale_id,
                unsupported_number_systems_string,
            ))

        write_datafile(data_filename, data, dump_json=dump_json)


def _should_skip_number_elem(data, elem):
    """
    Figure out whether the numbering-containing element `elem` is in a currently
    non-supported (i.e. currently non-Latin) numbering system.

    :param data: The root data element, for stashing the warning.
    :param elem: Element with `numberSystem` key
    :return: Boolean
    """
    number_system = elem.get('numberSystem', 'latn')

    if number_system != 'latn':
        data['unsupported_number_systems'].add(number_system)
        return True

    return False


def _should_skip_elem(elem, type=None, dest=None):
    """
    Check whether the given element should be skipped.

    Elements are skipped if they are drafts or alternates of data that already exists in `dest`.

    :param elem: XML element
    :param type: Type string. May be elided if the dest dict is elided.
    :param dest: Destination dict. May be elided to skip the dict check.
    :return: skip boolean
    """
    if 'draft' in elem.attrib or 'alt' in elem.attrib:
        if dest is None or type in dest:
            return True


def _import_type_text(dest, elem, type=None):
    """
    Conditionally import the element's inner text(s) into the `dest` dict.

    The condition being, namely, that the element isn't a draft/alternate version
    of a pre-existing element.

    :param dest: Destination dict
    :param elem: XML element.
    :param type: Override type. (By default, the `type` attr of the element.)
    :return:
    """
    if type is None:
        type = elem.attrib['type']
    if _should_skip_elem(elem, type, dest):
        return
    dest[type] = _text(elem)


def parse_locale_display_names(data, tree):
    territories = data.setdefault('territories', {})
    for elem in tree.findall('.//territories/territory'):
        _import_type_text(territories, elem)
    languages = data.setdefault('languages', {})
    for elem in tree.findall('.//languages/language'):
        _import_type_text(languages, elem)
    variants = data.setdefault('variants', {})
    for elem in tree.findall('.//variants/variant'):
        _import_type_text(variants, elem)
    scripts = data.setdefault('scripts', {})
    for elem in tree.findall('.//scripts/script'):
        _import_type_text(scripts, elem)


def parse_list_patterns(data, tree):
    list_patterns = data.setdefault('list_patterns', {})
    for listType in tree.findall('.//listPatterns/listPattern'):
        by_type = list_patterns.setdefault(listType.attrib.get('type', 'standard'), {})
        for listPattern in listType.findall('listPatternPart'):
            by_type[listPattern.attrib['type']] = _text(listPattern)


def parse_dates(data, tree, sup, regions, territory):
    week_data = data.setdefault('week_data', {})
    supelem = sup.find('.//weekData')
    for elem in supelem.findall('minDays'):
        if _should_skip_elem(elem):
            continue
        territories = elem.attrib['territories'].split()
        if territory in territories or any([r in territories for r in regions]):
            week_data['min_days'] = int(elem.attrib['count'])
    for elem in supelem.findall('firstDay'):
        if _should_skip_elem(elem):
            continue
        territories = elem.attrib['territories'].split()
        if territory in territories or any([r in territories for r in regions]):
            week_data['first_day'] = weekdays[elem.attrib['day']]
    for elem in supelem.findall('weekendStart'):
        if _should_skip_elem(elem):
            continue
        territories = elem.attrib['territories'].split()
        if territory in territories or any([r in territories for r in regions]):
            week_data['weekend_start'] = weekdays[elem.attrib['day']]
    for elem in supelem.findall('weekendEnd'):
        if _should_skip_elem(elem):
            continue
        territories = elem.attrib['territories'].split()
        if territory in territories or any([r in territories for r in regions]):
            week_data['weekend_end'] = weekdays[elem.attrib['day']]
    zone_formats = data.setdefault('zone_formats', {})
    for elem in tree.findall('.//timeZoneNames/gmtFormat'):
        if not _should_skip_elem(elem):
            zone_formats['gmt'] = text_type(elem.text).replace('{0}', '%s')
            break
    for elem in tree.findall('.//timeZoneNames/regionFormat'):
        if not _should_skip_elem(elem):
            zone_formats['region'] = text_type(elem.text).replace('{0}', '%s')
            break
    for elem in tree.findall('.//timeZoneNames/fallbackFormat'):
        if not _should_skip_elem(elem):
            zone_formats['fallback'] = (
                text_type(elem.text).replace('{0}', '%(0)s').replace('{1}', '%(1)s')
            )
            break
    for elem in tree.findall('.//timeZoneNames/fallbackRegionFormat'):
        if not _should_skip_elem(elem):
            zone_formats['fallback_region'] = (
                text_type(elem.text).replace('{0}', '%(0)s').replace('{1}', '%(1)s')
            )
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


def parse_calendar_months(data, calendar):
    months = data.setdefault('months', {})
    for ctxt in calendar.findall('months/monthContext'):
        ctxt_type = ctxt.attrib['type']
        ctxts = months.setdefault(ctxt_type, {})
        for width in ctxt.findall('monthWidth'):
            width_type = width.attrib['type']
            widths = ctxts.setdefault(width_type, {})
            for elem in width:
                if elem.tag == 'month':
                    _import_type_text(widths, elem, int(elem.attrib['type']))
                elif elem.tag == 'alias':
                    ctxts[width_type] = Alias(
                        _translate_alias(['months', ctxt_type, width_type],
                                         elem.attrib['path'])
                    )


def parse_calendar_days(data, calendar):
    days = data.setdefault('days', {})
    for ctxt in calendar.findall('days/dayContext'):
        ctxt_type = ctxt.attrib['type']
        ctxts = days.setdefault(ctxt_type, {})
        for width in ctxt.findall('dayWidth'):
            width_type = width.attrib['type']
            widths = ctxts.setdefault(width_type, {})
            for elem in width:
                if elem.tag == 'day':
                    _import_type_text(widths, elem, weekdays[elem.attrib['type']])
                elif elem.tag == 'alias':
                    ctxts[width_type] = Alias(
                        _translate_alias(['days', ctxt_type, width_type],
                                         elem.attrib['path'])
                    )


def parse_calendar_quarters(data, calendar):
    quarters = data.setdefault('quarters', {})
    for ctxt in calendar.findall('quarters/quarterContext'):
        ctxt_type = ctxt.attrib['type']
        ctxts = quarters.setdefault(ctxt.attrib['type'], {})
        for width in ctxt.findall('quarterWidth'):
            width_type = width.attrib['type']
            widths = ctxts.setdefault(width_type, {})
            for elem in width:
                if elem.tag == 'quarter':
                    _import_type_text(widths, elem, int(elem.attrib['type']))
                elif elem.tag == 'alias':
                    ctxts[width_type] = Alias(
                        _translate_alias(['quarters', ctxt_type,
                                          width_type],
                                         elem.attrib['path']))


def parse_calendar_eras(data, calendar):
    eras = data.setdefault('eras', {})
    for width in calendar.findall('eras/*'):
        width_type = NAME_MAP[width.tag]
        widths = eras.setdefault(width_type, {})
        for elem in width:
            if elem.tag == 'era':
                _import_type_text(widths, elem, type=int(elem.attrib.get('type')))
            elif elem.tag == 'alias':
                eras[width_type] = Alias(
                    _translate_alias(['eras', width_type],
                                     elem.attrib['path'])
                )


def parse_calendar_periods(data, calendar):
    # Day periods (AM/PM/others)
    periods = data.setdefault('day_periods', {})
    for day_period_ctx in calendar.findall('dayPeriods/dayPeriodContext'):
        ctx_type = day_period_ctx.attrib["type"]
        for day_period_width in day_period_ctx.findall('dayPeriodWidth'):
            width_type = day_period_width.attrib["type"]
            dest_dict = periods.setdefault(ctx_type, {}).setdefault(width_type, {})
            for day_period in day_period_width.findall('dayPeriod'):
                period_type = day_period.attrib['type']
                if 'alt' not in day_period.attrib:
                    dest_dict[period_type] = text_type(day_period.text)


def parse_calendar_date_formats(data, calendar):
    date_formats = data.setdefault('date_formats', {})
    for format in calendar.findall('dateFormats'):
        for elem in format:
            if elem.tag == 'dateFormatLength':
                type = elem.attrib.get('type')
                if _should_skip_elem(elem, type, date_formats):
                    continue
                try:
                    date_formats[type] = dates.parse_pattern(
                        text_type(elem.findtext('dateFormat/pattern'))
                    )
                except ValueError as e:
                    log.error(e)
            elif elem.tag == 'alias':
                date_formats = Alias(_translate_alias(
                    ['date_formats'], elem.attrib['path'])
                )


def parse_calendar_time_formats(data, calendar):
    time_formats = data.setdefault('time_formats', {})
    for format in calendar.findall('timeFormats'):
        for elem in format:
            if elem.tag == 'timeFormatLength':
                type = elem.attrib.get('type')
                if _should_skip_elem(elem, type, time_formats):
                    continue
                try:
                    time_formats[type] = dates.parse_pattern(
                        text_type(elem.findtext('timeFormat/pattern'))
                    )
                except ValueError as e:
                    log.error(e)
            elif elem.tag == 'alias':
                time_formats = Alias(_translate_alias(
                    ['time_formats'], elem.attrib['path'])
                )


def parse_calendar_datetime_skeletons(data, calendar):
    datetime_formats = data.setdefault('datetime_formats', {})
    datetime_skeletons = data.setdefault('datetime_skeletons', {})
    for format in calendar.findall('dateTimeFormats'):
        for elem in format:
            if elem.tag == 'dateTimeFormatLength':
                type = elem.attrib.get('type')
                if _should_skip_elem(elem, type, datetime_formats):
                    continue
                try:
                    datetime_formats[type] = text_type(elem.findtext('dateTimeFormat/pattern'))
                except ValueError as e:
                    log.error(e)
            elif elem.tag == 'alias':
                datetime_formats = Alias(_translate_alias(
                    ['datetime_formats'], elem.attrib['path'])
                )
            elif elem.tag == 'availableFormats':
                for datetime_skeleton in elem.findall('dateFormatItem'):
                    datetime_skeletons[datetime_skeleton.attrib['id']] = (
                        dates.parse_pattern(text_type(datetime_skeleton.text))
                    )


def parse_number_symbols(data, tree):
    number_symbols = data.setdefault('number_symbols', {})
    for symbol_elem in tree.findall('.//numbers/symbols'):
        if _should_skip_number_elem(data, symbol_elem):  # TODO: Support other number systems
            continue

        for elem in symbol_elem.findall('./*'):
            if _should_skip_elem(elem):
                continue
            number_symbols[elem.tag] = text_type(elem.text)


def parse_decimal_formats(data, tree):
    decimal_formats = data.setdefault('decimal_formats', {})
    for df_elem in tree.findall('.//decimalFormats'):
        if _should_skip_number_elem(data, df_elem):  # TODO: Support other number systems
            continue
        for elem in df_elem.findall('./decimalFormatLength'):
            length_type = elem.attrib.get('type')
            if _should_skip_elem(elem, length_type, decimal_formats):
                continue
            if elem.findall('./alias'):
                # TODO map the alias to its target
                continue
            for pattern_el in elem.findall('./decimalFormat/pattern'):
                pattern_type = pattern_el.attrib.get('type')
                pattern = numbers.parse_pattern(text_type(pattern_el.text))
                if pattern_type:
                    # This is a compact decimal format, see:
                    # https://www.unicode.org/reports/tr35/tr35-45/tr35-numbers.html#Compact_Number_Formats

                    # These are mapped into a `compact_decimal_formats` dictionary
                    # with the format {length: {count: {multiplier: pattern}}}.

                    # TODO: Add support for formatting them.
                    compact_decimal_formats = data.setdefault('compact_decimal_formats', {})
                    length_map = compact_decimal_formats.setdefault(length_type, {})
                    length_count_map = length_map.setdefault(pattern_el.attrib['count'], {})
                    length_count_map[pattern_type] = pattern
                else:
                    # Regular decimal format.
                    decimal_formats[length_type] = pattern


def parse_scientific_formats(data, tree):
    scientific_formats = data.setdefault('scientific_formats', {})
    for sf_elem in tree.findall('.//scientificFormats'):
        if _should_skip_number_elem(data, sf_elem):  # TODO: Support other number systems
            continue
        for elem in sf_elem.findall('./scientificFormatLength'):
            type = elem.attrib.get('type')
            if _should_skip_elem(elem, type, scientific_formats):
                continue
            pattern = text_type(elem.findtext('scientificFormat/pattern'))
            scientific_formats[type] = numbers.parse_pattern(pattern)


def parse_percent_formats(data, tree):
    percent_formats = data.setdefault('percent_formats', {})

    for pf_elem in tree.findall('.//percentFormats'):
        if _should_skip_number_elem(data, pf_elem):  # TODO: Support other number systems
            continue
        for elem in pf_elem.findall('.//percentFormatLength'):
            type = elem.attrib.get('type')
            if _should_skip_elem(elem, type, percent_formats):
                continue
            pattern = text_type(elem.findtext('percentFormat/pattern'))
            percent_formats[type] = numbers.parse_pattern(pattern)


def parse_currency_names(data, tree):
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
        for symbol in elem.findall('symbol'):
            if 'draft' in symbol.attrib or 'choice' in symbol.attrib:  # Skip drafts and choice-patterns
                continue
            if symbol.attrib.get('alt'):  # Skip alternate forms
                continue
            currency_symbols[code] = text_type(symbol.text)


def parse_unit_patterns(data, tree):
    unit_patterns = data.setdefault('unit_patterns', {})
    compound_patterns = data.setdefault('compound_unit_patterns', {})
    unit_display_names = data.setdefault('unit_display_names', {})

    for elem in tree.findall('.//units/unitLength'):
        unit_length_type = elem.attrib['type']
        for unit in elem.findall('unit'):
            unit_type = unit.attrib['type']
            unit_and_length_patterns = unit_patterns.setdefault(unit_type, {}).setdefault(unit_length_type, {})
            for pattern in unit.findall('unitPattern'):
                unit_and_length_patterns[pattern.attrib['count']] = _text(pattern)

            per_unit_pat = unit.find('perUnitPattern')
            if per_unit_pat is not None:
                unit_and_length_patterns['per'] = _text(per_unit_pat)

            display_name = unit.find('displayName')
            if display_name is not None:
                unit_display_names.setdefault(unit_type, {})[unit_length_type] = _text(display_name)

        for unit in elem.findall('compoundUnit'):
            unit_type = unit.attrib['type']
            compound_unit_info = {}
            compound_variations = {}
            for child in unit:
                if child.tag == "unitPrefixPattern":
                    compound_unit_info['prefix'] = _text(child)
                elif child.tag == "compoundUnitPattern":
                    compound_variations[None] = _text(child)
                elif child.tag == "compoundUnitPattern1":
                    compound_variations[child.attrib.get('count')] = _text(child)
            if compound_variations:
                compound_variation_values = set(compound_variations.values())
                if len(compound_variation_values) == 1:
                    # shortcut: if all compound variations are the same, only store one
                    compound_unit_info['compound'] = next(iter(compound_variation_values))
                else:
                    compound_unit_info['compound_variations'] = compound_variations
            compound_patterns.setdefault(unit_type, {})[unit_length_type] = compound_unit_info


def parse_date_fields(data, tree):
    date_fields = data.setdefault('date_fields', {})
    for elem in tree.findall('.//dates/fields/field'):
        field_type = elem.attrib['type']
        date_fields.setdefault(field_type, {})
        for rel_time in elem.findall('relativeTime'):
            rel_time_type = rel_time.attrib['type']
            for pattern in rel_time.findall('relativeTimePattern'):
                type_dict = date_fields[field_type].setdefault(rel_time_type, {})
                type_dict[pattern.attrib['count']] = text_type(pattern.text)


def parse_interval_formats(data, tree):
    # https://www.unicode.org/reports/tr35/tr35-dates.html#intervalFormats
    interval_formats = data.setdefault("interval_formats", {})
    for elem in tree.findall("dateTimeFormats/intervalFormats/*"):
        if 'draft' in elem.attrib:
            continue
        if elem.tag == "intervalFormatFallback":
            interval_formats[None] = elem.text
        elif elem.tag == "intervalFormatItem":
            skel_data = interval_formats.setdefault(elem.attrib["id"], {})
            for item_sub in elem:
                if item_sub.tag == "greatestDifference":
                    skel_data[item_sub.attrib["id"]] = split_interval_pattern(item_sub.text)
                else:
                    raise NotImplementedError("Not implemented: %s(%r)" % (item_sub.tag, item_sub.attrib))


def parse_currency_formats(data, tree):
    currency_formats = data.setdefault('currency_formats', {})
    for currency_format in tree.findall('.//currencyFormats'):
        if _should_skip_number_elem(data, currency_format):  # TODO: Support other number systems
            continue

        for length_elem in currency_format.findall('./currencyFormatLength'):
            curr_length_type = length_elem.attrib.get('type')
            for elem in length_elem.findall('currencyFormat'):
                type = elem.attrib.get('type')
                if curr_length_type:
                    # Handle `<currencyFormatLength type="short">`, etc.
                    # TODO(3.x): use nested dicts instead of colon-separated madness
                    type = '%s:%s' % (type, curr_length_type)
                if _should_skip_elem(elem, type, currency_formats):
                    continue
                for child in elem.iter():
                    if child.tag == 'alias':
                        currency_formats[type] = Alias(
                            _translate_alias(['currency_formats', elem.attrib['type']],
                                             child.attrib['path'])
                        )
                    elif child.tag == 'pattern':
                        pattern = text_type(child.text)
                        currency_formats[type] = numbers.parse_pattern(pattern)


def parse_currency_unit_patterns(data, tree):
    currency_unit_patterns = data.setdefault('currency_unit_patterns', {})
    for currency_formats_elem in tree.findall('.//currencyFormats'):
        if _should_skip_number_elem(data, currency_formats_elem):  # TODO: Support other number systems
            continue
        for unit_pattern_elem in currency_formats_elem.findall('./unitPattern'):
            count = unit_pattern_elem.attrib['count']
            pattern = text_type(unit_pattern_elem.text)
            currency_unit_patterns[count] = pattern


def parse_day_period_rules(tree):
    """
    Parse dayPeriodRule data into a dict.

    :param tree: ElementTree
    """
    day_periods = {}
    for ruleset in tree.findall(".//dayPeriodRuleSet"):
        ruleset_type = ruleset.attrib.get("type")  # None|"selection"
        for rules in ruleset.findall("dayPeriodRules"):
            locales = rules.attrib["locales"].split()
            for rule in rules.findall("dayPeriodRule"):
                type = rule.attrib["type"]
                if type in ("am", "pm"):  # These fixed periods are handled separately by `get_period_id`
                    continue
                rule = _compact_dict(dict(
                    (key, _time_to_seconds_past_midnight(rule.attrib.get(key)))
                    for key in ("after", "at", "before", "from", "to")
                ))
                for locale in locales:
                    dest_list = day_periods.setdefault(locale, {}).setdefault(ruleset_type, {}).setdefault(type, [])
                    dest_list.append(rule)
    return day_periods


def parse_character_order(data, tree):
    for elem in tree.findall('.//layout/orientation/characterOrder'):
        data['character_order'] = elem.text


def parse_measurement_systems(data, tree):
    measurement_systems = data.setdefault('measurement_systems', {})
    for measurement_system in tree.findall('.//measurementSystemNames/measurementSystemName'):
        type = measurement_system.attrib['type']
        if not _should_skip_elem(measurement_system, type=type, dest=measurement_systems):
            _import_type_text(measurement_systems, measurement_system, type=type)



if __name__ == '__main__':
    main()
