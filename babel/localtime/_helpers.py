try:
    import zoneinfo
except ModuleNotFoundError:
    zoneinfo = None
    import pytz


def _get_tzinfo(tzenv):
    """Get the tzinfo from `zoneinfo` or `pytz`

    :param tzenv: timezone in the form of Continent/City
    :return: tzinfo object or None if not found
    """
    if zoneinfo:
        try:
            return zoneinfo.ZoneInfo(tzenv)
        except zoneinfo.ZoneInfoNotFoundError:
            pass

    else:
        try:
            return pytz.timezone(tzenv)
        except pytz.UnknownTimeZoneError:
            pass

    return None

def _get_tzinfo_or_raise(tzenv):
    tzinfo = _get_tzinfo(tzenv)
    if tzinfo is None:
        raise LookupError(
            f"Can not find timezone {tzenv}. \n"
            "Please use a timezone in the form of Continent/City"
        )
    return tzinfo


def _get_tzinfo_from_file(tzfilename):
    with open(tzfilename, 'rb') as tzfile:
        if zoneinfo:
            return zoneinfo.ZoneInfo.from_file(tzfile)
        else:
            return pytz.tzfile.build_tzinfo('local', tzfile)
