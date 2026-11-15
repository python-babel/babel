import zoneinfo


def _get_tzinfo(tzenv: str):
    """Get the tzinfo from `zoneinfo`

    :param tzenv: timezone in the form of Continent/City
    :return: tzinfo object or None if not found
    """
    try:
        return zoneinfo.ZoneInfo(tzenv)
    except (zoneinfo.ZoneInfoNotFoundError, ValueError):
        # ValueError is raised for malformed keys.
        # If that happens, we pretend it meant that the TZ didn't exist,
        # for the benefit of `babel.localtime` catching the `LookupError`
        # raised by `_get_tzinfo_or_raise()`.
        # See https://github.com/python-babel/babel/issues/1092
        return None


def _get_tzinfo_or_raise(tzenv: str):
    tzinfo = _get_tzinfo(tzenv)
    if tzinfo is None:
        raise LookupError(
            f"Can not find timezone {tzenv}. \n"
            "Timezone names are generally in the form `Continent/City`.",
        )
    return tzinfo


def _get_tzinfo_from_file(tzfilename: str):
    with open(tzfilename, 'rb') as tzfile:
        return zoneinfo.ZoneInfo.from_file(tzfile)
