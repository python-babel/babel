Babel Development
=================

Babel as a library has a long history that goes back to the Trac project.
Since then it has evolved into an independently developed project that
implements data access for the CLDR project.

This document tries to explain as best as possible the general rules of
the project in case you want to help out developing.

Tracking the CLDR
-----------------

Generally the goal of the project is to work as closely as possible with
the CLDR data.  This has in the past caused some frustrating problems
because the data is entirely out of our hand.  To minimize the frustration
we generally deal with CLDR updates the following way:

*   bump the CLDR data only with a major release of Babel.
*   never perform custom bugfixes on the CLDR data.
*   never work around CLDR bugs within Babel.  If you find a problem in
    the data, report it upstream.
*   adjust the parsing of the data as soon as possible, otherwise this
    will spiral out of control later.  This is especially the case for
    bigger updates that change pluralization and more.
*   try not to test against specific CLDR data that is likely to change.

Python Versions
---------------

At the moment the following Python versions should be supported:

*   Python 2.7
*   Python 3.4 and up
*   PyPy tracking 2.7 and 3.2 and up

While PyPy does not currently support 3.3, it does support traditional
unicode literals which simplifies the entire situation tremendously.

Documentation must build on Python 2, Python 3 support for the
documentation is an optional goal.  Code examples in the docs preferably
are written in a style that makes them work on both 2.x and 3.x with
preference to the former.

Unicode
-------

Unicode is a big deal in Babel.  Here is how the rules are set up:

*   internally everything is unicode that makes sense to have as unicode.
    The exception to this rule are things which on Python 2 traditionally
    have been bytes.  For example file names on Python 2 should be treated
    as bytes wherever possible.
*   Encode / decode at boundaries explicitly.  Never assume an encoding in
    a way it cannot be overridden.  utf-8 should be generally considered
    the default encoding.
*   Dot not use ``unicode_literals``, instead use the ``u''`` string
    syntax.  The reason for this is that the former introduces countless
    of unicode problems by accidentally upgrading strings to unicode which
    should not be.  (docstrings for instance).

Dates and Timezones
-------------------

Generally all timezone support in Babel is based on pytz which it just
depends on.  Babel should assume that timezone objects are pytz based
because those are the only ones with an API that actually work correctly
(due to the API problems with non UTC based timezones).

Assumptions to make:

*   use UTC where possible.
*   be super careful with local time.  Do not use local time without
    knowing the exact timezone.
*   `time` without date is a very useless construct.  Do not try to
    support timezones for it.  If you do, assume that the current local
    date is assumed and not utc date.
