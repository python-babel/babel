""" Unit tests for the 'localtime' module.

There are separate test cases for Unix and Win32, only one of which will be
executed.

"""
import datetime
import os.path
import sys
from pathlib import Path

import pytest

from babel.localtime import LOCALTZ, get_localzone

_timezones = {
    "Etc/UTC": "UTC",
    "America/New_York": "EDT",  # DST
    "Europe/Paris": "CEST",  # DST
}


@pytest.mark.skipif(sys.platform == "win32", reason="Unix tests")
@pytest.mark.usefixtures("fs")  # provided by 'pyfakefs'
class TestUnixLocaltime:
    """ Tests for the `localtime` module in a Unix environment.

    Unix relies heavily on files to configure the system time zone, so the
    'pyfakefs' library is used here to isolate tests from the local file
    system: <https://pypi.org/project/pyfakefs/>.

    """
    @pytest.fixture
    def zoneinfo(self, fs) -> Path:
        """ Provide access to the system TZ info directory.

        :return: directory path
        """
        # Reproducing a working zoneinfo database in the test environment would
        # be a hassle, so add access to the system database. This assumes the
        # test system follows the convention of linking `/etc/localtime` to the
        # system's TZ info file somewhere in a `zoneinfo/` hierarchy.
        # <https://www.unix.com/man-page/linux/4/zoneinfo>
        fs.add_real_symlink("/etc/localtime")
        parts = list(Path("/etc/localtime").readlink().parts)
        while parts and parts[-1] != "zoneinfo":
            # Find the 'zoneinfo' root.
            del parts[-1]
        zoneinfo = Path(*parts)
        fs.add_real_directory(zoneinfo)
        return zoneinfo

    @pytest.fixture(params=_timezones.items())
    def timezone(self, zoneinfo, request) -> str:
        """ Set the test time zone.

        :return: time zone name, *i.e..* ZoneInfo.tzname()
        """
        # As with the `zoneinfo` fixture, this assumes the test system uses a
        # standard-ish Unix implementation where `/etc/localtime` can be used
        # to set the time zone.
        # <https://www.unix.com/man-page/linux/4/zoneinfo>
        #
        # Note the double slash in the symlink source. Because os.symlink()
        # does not normalize paths, this will appear on the file system as
        # e.g. `zoneinfo//Etc/UTC`. Although irregular, this is a valid link
        # and has been observed in certain Ubuntu installations, so make sure
        # 'localtime' can handle them.
        # <https://github.com/python-babel/babel/issues/990>.
        key, name = request.param
        os.remove("/etc/localtime")
        os.symlink(f"{zoneinfo}//{key}", "/etc/localtime")  # double slash OK
        return name

    def test_get_localzone(self, zoneinfo, timezone):
        """ Test the get_localtime() function.

        """
        dst = datetime.datetime(2023, 7, 1)  # testing DST time zone names
        assert get_localzone().tzname(dst) == timezone

    def test_localtz(self, zoneinfo):
        """ Test the LOCALTZ module attribute.

        """
        assert get_localzone() == LOCALTZ


@pytest.mark.skipif(sys.platform != "win32", reason="Win32 tests")
class TestWin32Localtime:
    """ Tests for the `localtime` module in a Windows environment.

    """
    # This is just a placeholder and basic smoke test for now.
    # TODO: Add relevant tests.
    def test_localtz(self):
        """ Test the LOCALTZ module attribute.

        """
        assert get_localzone() == LOCALTZ
