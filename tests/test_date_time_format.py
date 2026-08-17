from datetime import date, datetime, time

from babel.dates import DateTimeFormat, _localize


def test_quarter_format():
    d = date(2006, 6, 8)
    fmt = DateTimeFormat(d, locale='en_US')
    assert fmt['Q'] == '2'
    assert fmt['QQQQ'] == '2nd quarter'
    assert fmt['q'] == '2'
    assert fmt['qqqq'] == '2nd quarter'
    d = date(2006, 12, 31)
    fmt = DateTimeFormat(d, locale='en_US')
    assert fmt['qqq'] == 'Q4'
    assert fmt['qqqqq'] == '4'
    assert fmt['QQQ'] == 'Q4'
    assert fmt['QQQQQ'] == '4'


def test_month_context():
    d = date(2006, 2, 8)
    assert DateTimeFormat(d, locale='mt_MT')['MMMMM'] == 'F'  # narrow format
    assert DateTimeFormat(d, locale='mt_MT')['LLLLL'] == 'Fr'  # narrow standalone


def test_abbreviated_month_alias():
    d = date(2006, 3, 8)
    assert DateTimeFormat(d, locale='de_DE')['LLL'] == 'Mär'


def test_week_of_year_first():
    d = date(2006, 1, 8)
    assert DateTimeFormat(d, locale='de_DE')['w'] == '1'
    assert DateTimeFormat(d, locale='en_US')['ww'] == '02'


def test_week_of_year_first_with_year():
    d = date(2006, 1, 1)
    fmt = DateTimeFormat(d, locale='de_DE')
    assert fmt['w'] == '52'
    assert fmt['YYYY'] == '2005'


def test_week_of_year_last():
    d = date(2006, 12, 26)
    assert DateTimeFormat(d, locale='de_DE')['w'] == '52'
    assert DateTimeFormat(d, locale='en_US')['w'] == '52'


def test_week_of_year_last_us_extra_week():
    d = date(2005, 12, 26)
    assert DateTimeFormat(d, locale='de_DE')['w'] == '52'
    assert DateTimeFormat(d, locale='en_US')['w'] == '53'


def test_week_of_year_de_first_us_last_with_year():
    d = date(2018, 12, 31)
    fmt = DateTimeFormat(d, locale='de_DE')
    assert fmt['w'] == '1'
    assert fmt['YYYY'] == '2019'
    fmt = DateTimeFormat(d, locale='en_US')
    # See 363ad753, issue #1179
    assert fmt['w'] == '1'
    assert fmt['YYYY'] == '2019'


def test_week_of_month_first():
    d = date(2006, 1, 8)
    assert DateTimeFormat(d, locale='de_DE')['W'] == '1'
    assert DateTimeFormat(d, locale='en_US')['W'] == '2'


def test_week_of_month_last():
    d = date(2006, 1, 29)
    assert DateTimeFormat(d, locale='de_DE')['W'] == '4'
    assert DateTimeFormat(d, locale='en_US')['W'] == '5'


def test_day_of_year():
    d = date(2007, 4, 1)
    assert DateTimeFormat(d, locale='en_US')['D'] == '91'


def test_day_of_year_works_with_datetime():
    d = datetime(2007, 4, 1)
    assert DateTimeFormat(d, locale='en_US')['D'] == '91'


def test_day_of_year_first():
    d = date(2007, 1, 1)
    assert DateTimeFormat(d, locale='en_US')['DDD'] == '001'


def test_day_of_year_last():
    d = date(2007, 12, 31)
    assert DateTimeFormat(d, locale='en_US')['DDD'] == '365'


def test_day_of_week_in_month():
    d = date(2007, 4, 15)
    assert DateTimeFormat(d, locale='en_US')['F'] == '3'


def test_day_of_week_in_month_first():
    d = date(2007, 4, 1)
    assert DateTimeFormat(d, locale='en_US')['F'] == '1'


def test_day_of_week_in_month_last():
    d = date(2007, 4, 29)
    assert DateTimeFormat(d, locale='en_US')['F'] == '5'


def test_local_day_of_week():
    d = date(2007, 4, 1)  # a sunday
    assert DateTimeFormat(d, locale='de_DE')['e'] == '7'  # monday is first day of week
    assert DateTimeFormat(d, locale='en_US')['ee'] == '01'  # sunday is first day of week
    assert DateTimeFormat(d, locale='ar_BH')['ee'] == '02'  # saturday is first day of week

    d = date(2007, 4, 2)  # a monday
    assert DateTimeFormat(d, locale='de_DE')['e'] == '1'  # monday is first day of week
    assert DateTimeFormat(d, locale='en_US')['ee'] == '02'  # sunday is first day of week
    assert DateTimeFormat(d, locale='ar_BH')['ee'] == '03'  # saturday is first day of week


def test_local_day_of_week_standalone():
    d = date(2007, 4, 1)  # a sunday
    assert DateTimeFormat(d, locale='de_DE')['c'] == '7'  # monday is first day of week
    assert DateTimeFormat(d, locale='en_US')['c'] == '1'  # sunday is first day of week
    assert DateTimeFormat(d, locale='ar_BH')['c'] == '2'  # saturday is first day of week

    d = date(2007, 4, 2)  # a monday
    assert DateTimeFormat(d, locale='de_DE')['c'] == '1'  # monday is first day of week
    assert DateTimeFormat(d, locale='en_US')['c'] == '2'  # sunday is first day of week
    assert DateTimeFormat(d, locale='ar_BH')['c'] == '3'  # saturday is first day of week


def test_pattern_day_of_week():
    dt = datetime(2016, 2, 6)
    fmt = DateTimeFormat(dt, locale='en_US')
    assert fmt['c'] == '7'
    assert fmt['ccc'] == 'Sat'
    assert fmt['cccc'] == 'Saturday'
    assert fmt['ccccc'] == 'S'
    assert fmt['cccccc'] == 'Sa'
    assert fmt['e'] == '7'
    assert fmt['ee'] == '07'
    assert fmt['eee'] == 'Sat'
    assert fmt['eeee'] == 'Saturday'
    assert fmt['eeeee'] == 'S'
    assert fmt['eeeeee'] == 'Sa'
    assert fmt['E'] == 'Sat'
    assert fmt['EE'] == 'Sat'
    assert fmt['EEE'] == 'Sat'
    assert fmt['EEEE'] == 'Saturday'
    assert fmt['EEEEE'] == 'S'
    assert fmt['EEEEEE'] == 'Sa'
    fmt = DateTimeFormat(dt, locale='uk')
    assert fmt['c'] == '6'
    assert fmt['e'] == '6'
    assert fmt['ee'] == '06'


def test_fractional_seconds():
    t = time(8, 3, 9, 799)
    assert DateTimeFormat(t, locale='en_US')['S'] == '0'
    t = time(8, 3, 1, 799)
    assert DateTimeFormat(t, locale='en_US')['SSSS'] == '0008'
    t = time(8, 3, 1, 34567)
    assert DateTimeFormat(t, locale='en_US')['SSSS'] == '0346'
    t = time(8, 3, 1, 345678)
    assert DateTimeFormat(t, locale='en_US')['SSSSSS'] == '345678'
    t = time(8, 3, 1, 799)
    assert DateTimeFormat(t, locale='en_US')['SSSSS'] == '00080'


def test_fractional_seconds_zero():
    t = time(15, 30, 0)
    assert DateTimeFormat(t, locale='en_US')['SSSS'] == '0000'


def test_milliseconds_in_day():
    t = time(15, 30, 12, 345000)
    assert DateTimeFormat(t, locale='en_US')['AAAA'] == '55812345'


def test_milliseconds_in_day_zero():
    d = time(0, 0, 0)
    assert DateTimeFormat(d, locale='en_US')['AAAA'] == '0000'


def test_timezone_rfc822(timezone_getter):
    tz = timezone_getter('Europe/Berlin')
    t = _localize(tz, datetime(2015, 1, 1, 15, 30))
    assert DateTimeFormat(t, locale='de_DE')['Z'] == '+0100'


def test_timezone_gmt(timezone_getter):
    tz = timezone_getter('Europe/Berlin')
    t = _localize(tz, datetime(2015, 1, 1, 15, 30))
    assert DateTimeFormat(t, locale='de_DE')['ZZZZ'] == 'GMT+01:00'


def test_timezone_name(timezone_getter):
    tz = timezone_getter('Europe/Paris')
    dt = _localize(tz, datetime(2007, 4, 1, 15, 30))
    assert DateTimeFormat(dt, locale='fr_FR')['v'] == 'heure : France'


def test_timezone_location_format(timezone_getter):
    tz = timezone_getter('Europe/Paris')
    dt = _localize(tz, datetime(2007, 4, 1, 15, 30))
    assert DateTimeFormat(dt, locale='fr_FR')['VVVV'] == 'heure : France'


def test_timezone_walltime_short(timezone_getter):
    tz = timezone_getter('Europe/Paris')
    t = time(15, 30, tzinfo=tz)
    assert DateTimeFormat(t, locale='fr_FR')['v'] == 'heure : France'


def test_timezone_walltime_long(timezone_getter):
    tz = timezone_getter('Europe/Paris')
    t = time(15, 30, tzinfo=tz)
    assert DateTimeFormat(t, locale='fr_FR')['vvvv'] == 'heure d’Europe centrale'
