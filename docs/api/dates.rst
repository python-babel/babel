Date and Time
=============

.. module:: babel.dates

The date and time functionality provided by Babel lets you format standard
Python `datetime`, `date` and `time` objects and work with timezones.

Date and Time Formatting
------------------------

.. autofunction:: format_datetime(datetime=None, format='medium', tzinfo=None, locale=default_locale('LC_TIME'))

.. autofunction:: format_date(date=None, format='medium', locale=default_locale('LC_TIME'))

.. autofunction:: format_time(time=None, format='medium', tzinfo=None, locale=default_locale('LC_TIME'))

.. autofunction:: format_timedelta(delta, granularity='second', threshold=.85, add_direction=False, format='long', locale=default_locale('LC_TIME'))

.. autofunction:: format_skeleton(skeleton, datetime=None, tzinfo=None, fuzzy=True, locale=default_locale('LC_TIME'))

.. autofunction:: format_interval(start, end, skeleton=None, tzinfo=None, fuzzy=True, locale=default_locale('LC_TIME'))

Timezone Functionality
----------------------

.. autofunction:: get_timezone

.. autofunction:: get_timezone_gmt

.. autofunction:: get_timezone_location

.. autofunction:: get_timezone_name

.. autofunction:: get_next_timezone_transition

.. data:: UTC

    A timezone object for UTC.

.. data:: LOCALTZ

    A timezone object for the computer's local timezone.

Data Access
-----------

.. autofunction:: get_period_names

.. autofunction:: get_day_names

.. autofunction:: get_month_names

.. autofunction:: get_quarter_names

.. autofunction:: get_era_names

.. autofunction:: get_date_format

.. autofunction:: get_datetime_format

.. autofunction:: get_time_format

Basic Parsing
-------------

.. autofunction:: parse_date

.. autofunction:: parse_time

.. autofunction:: parse_pattern
