import datetime
from zoneinfo import ZoneInfo

import pytest

from babel import dates
from babel.util import UTC

TEST_DT = datetime.datetime(2016, 1, 8, 11, 46, 15)
TEST_TIME = TEST_DT.time()
TEST_DATE = TEST_DT.date()


@pytest.mark.parametrize(
    ("start", "end", "skeleton", "expected"),
    [
        (TEST_DT, TEST_DT, "yMMMd", "8.1.2016"),
        (TEST_DT, TEST_DT, "xxx", "8.1.2016 11.46.15"),
        (TEST_TIME, TEST_TIME, "xxx", "11.46.15"),
        (TEST_DATE, TEST_DATE, "xxx", "8.1.2016"),
    ],
)
def test_format_interval_same_instant(start, end, skeleton, expected):
    assert dates.format_interval(start, end, skeleton, fuzzy=False, locale="fi") == expected


def test_format_interval_no_difference():
    t1 = TEST_DT
    t2 = t1 + datetime.timedelta(minutes=8)
    assert dates.format_interval(t1, t2, "yMd", fuzzy=False, locale="fi") == "8.1.2016"


def test_format_interval_in_tz(timezone_getter):
    t1 = TEST_DT.replace(tzinfo=UTC)
    t2 = t1 + datetime.timedelta(minutes=18)
    hki_tz = timezone_getter("Europe/Helsinki")
    formatted = dates.format_interval(t1, t2, "Hmv", tzinfo=hki_tz, locale="fi")
    assert formatted == "13.46\u201314.04 aikavyöhyke: Suomi"


def test_format_interval_across_repeated_hour():
    # A 1-hour event spanning the autumn DST fall-back in New York
    # (01:15 EDT -> 01:15 EST) produces two datetimes that compare equal
    # under PEP 495 despite representing instants one hour apart.
    eastern = ZoneInfo("America/New_York")
    start_utc = datetime.datetime(2026, 11, 1, 5, 15, tzinfo=UTC)
    start = start_utc.astimezone(eastern)
    end = (start_utc + datetime.timedelta(hours=1)).astimezone(eastern)

    assert dates.format_interval(start, end, "hm", tzinfo=UTC, locale="en_US") == (
        "5:15\u2009\u2013\u20096:15\u202fAM"
    )


def test_format_interval_12_hour():
    t2 = TEST_DT
    t1 = t2 - datetime.timedelta(hours=1)
    formatted = dates.format_interval(t1, t2, "hm", locale="en")
    assert formatted == "10:46\u2009\u2013\u200911:46\u202fAM"


def test_format_interval_invalid_skeleton():
    t1 = TEST_DATE
    t2 = TEST_DATE + datetime.timedelta(days=1)
    formatted = dates.format_interval(t1, t2, "mumumu", fuzzy=False, locale="fi")
    assert formatted == "8.1.2016\u20139.1.2016"
    assert dates.format_interval(t1, t2, fuzzy=False, locale="fi") == "8.1.2016\u20139.1.2016"


def test_issue_825():
    formatted = dates.format_timedelta(
        datetime.timedelta(hours=1),
        granularity='hour',
        threshold=100,
        format='short',
        locale='pt',
    )
    assert formatted == '1 h'
