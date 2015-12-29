try:
    import _winreg as winreg
except ImportError:
    try:
        import winreg
    except ImportError:
        winreg = None

import pytz

# list interned from get_global("windows_zone_mapping")
# to avoid early load of global.dat.
# TODO: Add automatic importing for these?
tz_names = {
    "Afghanistan Standard Time": "Asia/Kabul",
    "Alaskan Standard Time": "America/Anchorage",
    "Arab Standard Time": "Asia/Riyadh",
    "Arabian Standard Time": "Asia/Dubai",
    "Arabic Standard Time": "Asia/Baghdad",
    "Argentina Standard Time": "America/Buenos_Aires",
    "Atlantic Standard Time": "America/Halifax",
    "AUS Central Standard Time": "Australia/Darwin",
    "AUS Eastern Standard Time": "Australia/Sydney",
    "Azerbaijan Standard Time": "Asia/Baku",
    "Azores Standard Time": "Atlantic/Azores",
    "Bahia Standard Time": "America/Bahia",
    "Bangladesh Standard Time": "Asia/Dhaka",
    "Belarus Standard Time": "Europe/Minsk",
    "Canada Central Standard Time": "America/Regina",
    "Cape Verde Standard Time": "Atlantic/Cape_Verde",
    "Caucasus Standard Time": "Asia/Yerevan",
    "Cen. Australia Standard Time": "Australia/Adelaide",
    "Central America Standard Time": "America/Guatemala",
    "Central Asia Standard Time": "Asia/Almaty",
    "Central Brazilian Standard Time": "America/Cuiaba",
    "Central Europe Standard Time": "Europe/Budapest",
    "Central European Standard Time": "Europe/Warsaw",
    "Central Pacific Standard Time": "Pacific/Guadalcanal",
    "Central Standard Time (Mexico)": "America/Mexico_City",
    "Central Standard Time": "America/Chicago",
    "China Standard Time": "Asia/Shanghai",
    "Dateline Standard Time": "Etc/GMT+12",
    "E. Africa Standard Time": "Africa/Nairobi",
    "E. Australia Standard Time": "Australia/Brisbane",
    "E. South America Standard Time": "America/Sao_Paulo",
    "Eastern Standard Time (Mexico)": "America/Cancun",
    "Eastern Standard Time": "America/New_York",
    "Egypt Standard Time": "Africa/Cairo",
    "Ekaterinburg Standard Time": "Asia/Yekaterinburg",
    "Fiji Standard Time": "Pacific/Fiji",
    "FLE Standard Time": "Europe/Kiev",
    "Georgian Standard Time": "Asia/Tbilisi",
    "GMT Standard Time": "Europe/London",
    "Greenland Standard Time": "America/Godthab",
    "Greenwich Standard Time": "Atlantic/Reykjavik",
    "GTB Standard Time": "Europe/Bucharest",
    "Hawaiian Standard Time": "Pacific/Honolulu",
    "India Standard Time": "Asia/Calcutta",
    "Iran Standard Time": "Asia/Tehran",
    "Israel Standard Time": "Asia/Jerusalem",
    "Jordan Standard Time": "Asia/Amman",
    "Kaliningrad Standard Time": "Europe/Kaliningrad",
    "Korea Standard Time": "Asia/Seoul",
    "Libya Standard Time": "Africa/Tripoli",
    "Line Islands Standard Time": "Pacific/Kiritimati",
    "Magadan Standard Time": "Asia/Magadan",
    "Mauritius Standard Time": "Indian/Mauritius",
    "Middle East Standard Time": "Asia/Beirut",
    "Montevideo Standard Time": "America/Montevideo",
    "Morocco Standard Time": "Africa/Casablanca",
    "Mountain Standard Time (Mexico)": "America/Chihuahua",
    "Mountain Standard Time": "America/Denver",
    "Myanmar Standard Time": "Asia/Rangoon",
    "N. Central Asia Standard Time": "Asia/Novosibirsk",
    "Namibia Standard Time": "Africa/Windhoek",
    "Nepal Standard Time": "Asia/Katmandu",
    "New Zealand Standard Time": "Pacific/Auckland",
    "Newfoundland Standard Time": "America/St_Johns",
    "North Asia East Standard Time": "Asia/Irkutsk",
    "North Asia Standard Time": "Asia/Krasnoyarsk",
    "Pacific SA Standard Time": "America/Santiago",
    "Pacific Standard Time (Mexico)": "America/Santa_Isabel",
    "Pacific Standard Time": "America/Los_Angeles",
    "Pakistan Standard Time": "Asia/Karachi",
    "Paraguay Standard Time": "America/Asuncion",
    "Romance Standard Time": "Europe/Paris",
    "Russia Time Zone 10": "Asia/Srednekolymsk",
    "Russia Time Zone 11": "Asia/Kamchatka",
    "Russia Time Zone 3": "Europe/Samara",
    "Russian Standard Time": "Europe/Moscow",
    "SA Eastern Standard Time": "America/Cayenne",
    "SA Pacific Standard Time": "America/Bogota",
    "SA Western Standard Time": "America/La_Paz",
    "Samoa Standard Time": "Pacific/Apia",
    "SE Asia Standard Time": "Asia/Bangkok",
    "Singapore Standard Time": "Asia/Singapore",
    "South Africa Standard Time": "Africa/Johannesburg",
    "Sri Lanka Standard Time": "Asia/Colombo",
    "Syria Standard Time": "Asia/Damascus",
    "Taipei Standard Time": "Asia/Taipei",
    "Tasmania Standard Time": "Australia/Hobart",
    "Tokyo Standard Time": "Asia/Tokyo",
    "Tonga Standard Time": "Pacific/Tongatapu",
    "Turkey Standard Time": "Europe/Istanbul",
    "Ulaanbaatar Standard Time": "Asia/Ulaanbaatar",
    "US Eastern Standard Time": "America/Indianapolis",
    "US Mountain Standard Time": "America/Phoenix",
    "UTC": "Etc/GMT",
    "UTC+12": "Etc/GMT-12",
    "UTC-02": "Etc/GMT+2",
    "UTC-11": "Etc/GMT+11",
    "Venezuela Standard Time": "America/Caracas",
    "Vladivostok Standard Time": "Asia/Vladivostok",
    "W. Australia Standard Time": "Australia/Perth",
    "W. Central Africa Standard Time": "Africa/Lagos",
    "W. Europe Standard Time": "Europe/Berlin",
    "West Asia Standard Time": "Asia/Tashkent",
    "West Pacific Standard Time": "Pacific/Port_Moresby",
    "Yakutsk Standard Time": "Asia/Yakutsk",
}

def valuestodict(key):
    """Convert a registry key's values to a dictionary."""
    dict = {}
    size = winreg.QueryInfoKey(key)[1]
    for i in range(size):
        data = winreg.EnumValue(key, i)
        dict[data[0]] = data[1]
    return dict


def get_localzone_name():
    # Windows is special. It has unique time zone names (in several
    # meanings of the word) available, but unfortunately, they can be
    # translated to the language of the operating system, so we need to
    # do a backwards lookup, by going through all time zones and see which
    # one matches.
    handle = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)

    TZLOCALKEYNAME = r'SYSTEM\CurrentControlSet\Control\TimeZoneInformation'
    localtz = winreg.OpenKey(handle, TZLOCALKEYNAME)
    keyvalues = valuestodict(localtz)
    localtz.Close()
    if 'TimeZoneKeyName' in keyvalues:
        # Windows 7 (and Vista?)

        # For some reason this returns a string with loads of NUL bytes at
        # least on some systems. I don't know if this is a bug somewhere, I
        # just work around it.
        tzkeyname = keyvalues['TimeZoneKeyName'].split('\x00', 1)[0]
    else:
        # Windows 2000 or XP

        # This is the localized name:
        tzwin = keyvalues['StandardName']

        # Open the list of timezones to look up the real name:
        TZKEYNAME = r'SOFTWARE\Microsoft\Windows NT\CurrentVersion\Time Zones'
        tzkey = winreg.OpenKey(handle, TZKEYNAME)

        # Now, match this value to Time Zone information
        tzkeyname = None
        for i in range(winreg.QueryInfoKey(tzkey)[0]):
            subkey = winreg.EnumKey(tzkey, i)
            sub = winreg.OpenKey(tzkey, subkey)
            data = valuestodict(sub)
            sub.Close()
            if data['Std'] == tzwin:
                tzkeyname = subkey
                break

        tzkey.Close()
        handle.Close()

    if tzkeyname is None:
        raise LookupError('Can not find Windows timezone configuration')

    timezone = tz_names.get(tzkeyname)
    if timezone is None:
        # Nope, that didn't work. Try adding 'Standard Time',
        # it seems to work a lot of times:
        timezone = tz_names.get(tzkeyname + ' Standard Time')

    # Return what we have.
    if timezone is None:
        raise pytz.UnknownTimeZoneError('Can not find timezone ' + tzkeyname)

    return timezone


def _get_localzone():
    if winreg is None:
        raise pytz.UnknownTimeZoneError(
            'Runtime support not available')
    return pytz.timezone(get_localzone_name())
