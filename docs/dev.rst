Babel Development
=================

Babel as a library has a long history that goes back to the Trac project.
Since then it has evolved into an independently developed project that
implements data access for the `https://cldr.unicode.org Unicode CLDR project`_.

This document tries to explain as best as possible the general rules of
the project in case you want to help out developing.

Tracking the CLDR
-----------------

Generally the goal of the project is to work as closely as possible with
the `https://cldr.unicode.org/index/charts CLDR data`_.  This has in the
past caused some frustrating problems
because the data is entirely out of our hand.  To minimize the frustration
we generally deal with CLDR updates the following way:

*   Bump the CLDR data only with a major release of Babel.
*   Never perform custom bugfixes on the CLDR data.
*   Never work around CLDR bugs within Babel. If you find a problem in
    the data, report it upstream.
*   Adjust the parsing of the data as soon as possible, otherwise this
    will spiral out of control later. This is especially the case for
    bigger updates that change pluralization and more.
*   Try not to test against specific CLDR data that is likely to change.

Python Versions
---------------

At the moment the following Python versions should be supported:

*   Python 3.8 and up
*   PyPy 3.8 and up

Unicode
-------

Unicode is a big deal in Babel. Here is how the rules are set up:

*   internally everything is unicode that makes sense to have as unicode.
*   Encode / decode at boundaries explicitly.  Never assume an encoding in
    a way it cannot be overridden.  utf-8 should be generally considered
    the default encoding.

Dates and Timezones
-------------------

Babel's timezone support relies on either ``pytz`` or ``zoneinfo``; if ``pytz``
is installed, it is preferred over ``zoneinfo``.  Babel should assume that any
timezone objects can be from either of these modules.

Assumptions to make:

*   use UTC where possible.
*   be super careful with local time.  Do not use local time without
    knowing the exact timezone.
*   `time` without date is a very useless construct.  Do not try to
    support timezones for it.  If you do, assume that the current local
    date is assumed and not utc date.
