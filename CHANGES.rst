Babel Changelog
===============

Version 2.17.0
--------------

Happy 2025! This release is being made from FOSDEM 2025, in Brussels, Belgium.

Thank you to all contributors, new and old,
and here's to another great year of internationalization and localization!

Features
~~~~~~~~

* CLDR: Babel now uses CLDR 46, by @tomasr8 in :gh:`1145`
* Dates: Allow specifying an explicit format in parse_date/parse_time by @tomasr8 in :gh:`1131`
* Dates: More alternate characters are now supported by `format_skeleton`. By @tomasr8 in :gh:`1122`
* Dates: Support short and narrow formats for format_timedelta when using `add_direction`, by @akx in :gh:`1163`
* Messages: .po files now enclose white spaces in filenames like GNU gettext does. By @Dunedan in :gh:`1105`, and @tomasr8 in :gh:`1120`
* Messages: Initial support for `Message.python_brace_format`, by @tomasr8 in :gh:`1169`
* Numbers: LC_MONETARY is now preferred when formatting currencies, by @akx in :gh:`1173`

Bugfixes
~~~~~~~~

* Dates: Make seconds optional in `parse_time` time formats by @tomasr8 in :gh:`1141`
* Dates: Replace `str.index` with `str.find` by @tomasr8 in :gh:`1130`
* Dates: Strip extra leading slashes in `/etc/localtime` by @akx in :gh:`1165`
* Dates: Week numbering and formatting of dates with week numbers was repaired by @jun66j5 in :gh:`1179`
* General: Improve handling for `locale=None` by @akx in :gh:`1164`
* General: Remove redundant assignment in `Catalog.__setitem__` by @tomasr8 in :gh:`1167`
* Messages: Fix extracted lineno with nested calls, by @dylankiss in :gh:`1126`
* Messages: Fix of list index out of range when translations is empty, by @gabe-sherman in :gh:`1135`
* Messages: Fix the way obsolete messages are stored by @tomasr8 in :gh:`1132`
* Messages: Simplify `read_mo` logic regarding `catalog.charset` by @tomasr8 in :gh:`1148`
* Messages: Use the first matching method & options, rather than first matching method & last options, by @jpmckinney in :gh:`1121`

Deprecation and compatibility
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Dates: Fix deprecation warnings for `datetime.utcnow()` by @tomasr8 in :gh:`1119`
* Docs: Adjust docs/conf.py to add compatibility with sphinx 8 by @hrnciar in :gh:`1155`
* General: Import `Literal` from the typing module by @tomasr8 in :gh:`1175`
* General: Replace `OrderedDict` with just `dict` by @tomasr8 in :gh:`1149`
* Messages: Mark `wraptext` deprecated; use `TextWrapper` directly in `write_po` by @akx in :gh:`1140`

Infrastructure
~~~~~~~~~~~~~~

* Add tzdata as dev dependency and sync with tox.ini by @wandrew004 in :gh:`1159`
* Duplicate test code was deleted by @mattdiaz007 in :gh:`1138`
* Increase test coverage of the `python_format` checker by @tomasr8 in :gh:`1176`
* Small cleanups by @akx in :gh:`1160`, :gh:`1166`, :gh:`1170` and :gh:`1172`
* Update CI to use python 3.13 and Ubuntu 24.04 by @tomasr8 in :gh:`1153`

Version 2.16.0
--------------

Features
~~~~~~~~

* CLDR: Upgrade to CLDR 45 by @tomasr8 in :gh:`1077`
* Lists: Support list format fallbacks by @akx in :gh:`1099`
* Messages: Initial support for reading mapping configuration as TOML by @akx in :gh:`1108`

Bugfixes
~~~~~~~~

* CLDR: Do not allow substituting alternates or drafts in derived locales by @akx in :gh:`1113`
* Core: Allow falling back to modifier-less locale data by @akx in :gh:`1104`
* Core: Allow use of importlib.metadata for finding entrypoints by @akx in :gh:`1102`
* Dates: Avoid crashing on importing localtime when TZ is malformed by @akx in :gh:`1100`
* Messages: Allow parsing .po files that have an extant but empty Language header by @akx in :gh:`1101`
* Messages: Fix ``--ignore-dirs`` being incorrectly read (#1094) by @john-psina and @Edwin18 in :gh:`1052` and :gh:`1095`
* Messages: Make pgettext search plurals when translation is not found by @tomasr8 in :gh:`1085`

Infrastructure
~~~~~~~~~~~~~~

* Replace deprecated `ast.Str` with `ast.Constant` by @tomasr8 in :gh:`1083`
* CI fixes by @akx in :gh:`1080`, :gh:`1097`, :gh:`1103`, :gh:`1107`
* Test on Python 3.13 beta releases by @akx in
* Normalize package name to lower-case in setup.py by @akx in :gh:`1110`

Documentation
~~~~~~~~~~~~~

* Add a mention to the docs that `format_skeleton(..., fuzzy=True)` may raise by @tomasr8 in :gh:`1106`
* Two hyperlinks (to CLDR) and some typos by @buhtz in :gh:`1115`


Version 2.15.0
--------------

Python version support
~~~~~~~~~~~~~~~~~~~~~~

* Babel 2.15.0 will require Python 3.8 or newer. (:gh:`1048`)

Features
~~~~~~~~

* CLDR: Upgrade to CLDR 44 (:gh:`1071`) (@akx)
* Dates: Support for the "fall back to short format" logic for time delta formatting (:gh:`1075`) (@akx)
* Message: More versatile .po IO functions (:gh:`1068`) (@akx)
* Numbers: Improved support for alternate spaces when parsing numbers (:gh:`1007`) (@ronnix's first contribution)

Infrastructure
~~~~~~~~~~~~~~

* Upgrade GitHub Actions (:gh:`1054`) (@cclauss's first contribution)
* The Unicode license is now included in `locale-data` and in the documentation (:gh:`1074`) (@akx)

Version 2.14.0
--------------

Upcoming deprecation
~~~~~~~~~~~~~~~~~~~~

* This version, Babel 2.14, is the last version of Babel to support Python 3.7.
  Babel 2.15 will require Python 3.8 or newer.
* We had previously announced Babel 2.13 to have been the last version to support
  Python 3.7, but being able to use CLDR 43 with Python 3.7 was deemed important
  enough to keep supporting the EOL Python version for one more release.

Possibly backwards incompatible changes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* ``Locale.number_symbols`` will now have first-level keys for each numbering system.
  Since the implicit default numbering system still is ``"latn"``, what had previously
  been e.g. ``Locale.number_symbols['decimal']`` is now ``Locale.number_symbols['latn']['decimal']``.
* Babel no longer directly depends on either ``distutils`` or ``setuptools``; if you had been
  using the Babel setuptools command extensions, you would need to explicitly depend on ``setuptools`` –
  though given you're running ``setup.py`` you probably already do.

Features
~~~~~~~~

* CLDR/Numbers: Add support of local numbering systems for number symbols by @kajte in :gh:`1036`
* CLDR: Upgrade to CLDR 43 by @rix0rrr in :gh:`1043`
* Frontend: Allow last_translator to be passed as an option to extract_message by @AivGitHub in :gh:`1044`
* Frontend: Decouple `pybabel` CLI frontend from distutils/setuptools by @akx in :gh:`1041`
* Numbers: Improve parsing of malformed decimals by @Olunusib and @akx in :gh:`1042`

Infrastructure
~~~~~~~~~~~~~~

* Enforce trailing commas (enable Ruff COM rule and autofix) by @akx in :gh:`1045`
* CI: use GitHub output formats by @akx in :gh:`1046`

Version 2.13.1
--------------

This is a patch release to fix a few bugs.

Fixes
~~~~~

* Fix a typo in ``_locales_to_names`` by @Dl84 in :gh:`1038` (issue :gh:`1037`)
* Fix ``setuptools`` dependency for Python 3.12 by @opryprin in :gh:`1033`

Version 2.13.0
--------------

Upcoming deprecation (reverted)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* It was previously announced that this version, Babel 2.13, would be the last version of
  Babel to support Python 3.7. Babel 2.14 will still support Python 3.7.

Features
~~~~~~~~

* Add flag to ignore POT-Creation-Date for updates by @joeportela in :gh:`999`
* Support 't' specifier in keywords by @jeanas in :gh:`1015`
* Add f-string parsing for Python 3.12 (PEP 701) by @encukou in :gh:`1027`

Fixes
~~~~~

* Various typing-related fixes by @akx in :gh:`979`, in :gh:`978`, :gh:`981`,  :gh:`983`
* babel.messages.catalog: deduplicate _to_fuzzy_match_key logic by @akx in :gh:`980`
* Freeze format_time() tests to a specific date to fix test failures by @mgorny in :gh:`998`
* Spelling and grammar fixes by @scop in :gh:`1008`
* Renovate lint tools by @akx in :gh:`1017`, :gh:`1028`
* Use SPDX license identifier by @vargenau in :gh:`994`
* Use aware UTC datetimes internally by @scop in :gh:`1009`

New Contributors
~~~~~~~~~~~~~~~~

* @mgorny made their first contribution in :gh:`998`
* @vargenau made their first contribution in :gh:`994`
* @joeportela made their first contribution in :gh:`999`
* @encukou made their first contribution in :gh:`1027`

Version 2.12.1
--------------

Fixes
~~~~~

* Version 2.12.0 was missing the ``py.typed`` marker file. Thanks to Alex Waygood for the fix! :gh:`975`
* The copyright year in all files was bumped to 2023.

Version 2.12.0
--------------

Deprecations & breaking changes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Python 3.6 is no longer supported (:gh:`919`) - Aarni Koskela
* The `get_next_timezone_transition` function is no more (:gh:`958`) - Aarni Koskela
* `Locale.parse()` will no longer return `None`; it will always return a Locale or raise an exception.
  Passing in `None`, though technically allowed by the typing, will raise. (:gh:`966`)

New features
~~~~~~~~~~~~

* CLDR: Babel now uses CLDR 42 (:gh:`951`) - Aarni Koskela
* Dates: `pytz` is now optional; Babel will prefer it but will use `zoneinfo` when available. (:gh:`940`) - @ds-cbo
* General: Babel now ships type annotations, thanks to Jonah Lawrence's work in multiple PRs.
* Locales: @modifiers are now retained when parsing locales (:gh:`947`) - martin f. krafft
* Messages: JavaScript template string expression extraction is now smarter. (:gh:`939`) - Johannes Wilm
* Numbers: NaN and Infinity are now better supported (:gh:`955`) - Jonah Lawrence
* Numbers: Short compact currency formats are now supported (:gh:`926`) - Jonah Lawrence
* Numbers: There's now a `Format.compact_decimal` utility function. (:gh:`921`) - Jonah Lawrence

Bugfixes
~~~~~~~~

* Dates: The cache for parsed datetime patterns is now bounded (:gh:`967`) - Aarni Koskela
* Messages: Fuzzy candidate matching accuracy is improved (:gh:`970`) - Jean Abou Samra
* Numbers: Compact singular formats and patterns with no numbers work correctly (:gh:`930`, :gh:`932`) - Jonah Lawrence, Jun Omae

Improvements & cleanup
~~~~~~~~~~~~~~~~~~~~~~

* Dates: `babel.dates.UTC` is now an alias for `datetime.timezone.utc` (:gh:`957`) - Aarni Koskela
* Dates: `babel.localtime` was slightly cleaned up. (:gh:`952`) - Aarni Koskela
* Documentation: Documentation was improved by Maciej Olko, Jonah Lawrence, lilinjie, and Aarni Koskela.
* Infrastructure: Babel is now being linted with pre-commit and ruff. - Aarni Koskela

Version 2.11.0
--------------

Upcoming deprecation
~~~~~~~~~~~~~~~~~~~~

* This version, Babel 2.11, is the last version of Babel to support Python 3.6.
  Babel 2.12 will require Python 3.7 or newer.

Improvements
~~~~~~~~~~~~

* Support for hex escapes in JavaScript string literals :gh:`877` - Przemyslaw Wegrzyn
* Add support for formatting decimals in compact form :gh:`909` - Jonah Lawrence
* Adapt parse_date to handle ISO dates in ASCII format :gh:`842` - Eric L.
* Use `ast` instead of `eval` for Python string extraction :gh:`915` - Aarni Koskela
    * This also enables extraction from static f-strings.
      F-strings with expressions are silently ignored (but won't raise an error as they used to).

Infrastructure
~~~~~~~~~~~~~~

* Tests: Use regular asserts and ``pytest.raises()`` :gh:`875` – Aarni Koskela
* Wheels are now built in GitHub Actions :gh:`888` – Aarni Koskela
* Small improvements to the CLDR downloader script :gh:`894` – Aarni Koskela
* Remove antiquated `__nonzero__` methods :gh:`896` - Nikita Sobolev
* Remove superfluous `__unicode__` declarations :gh:`905` - Lukas Juhrich
* Mark package compatible with Python 3.11 :gh:`913` - Aarni Koskela
* Quiesce pytest warnings :gh:`916` - Aarni Koskela

Bugfixes
~~~~~~~~

* Use email.Message for pofile header parsing instead of the deprecated ``cgi.parse_header`` function. :gh:`876` – Aarni Koskela
* Remove determining time zone via systemsetup on macOS :gh:`914` - Aarni Koskela

Documentation
~~~~~~~~~~~~~

* Update Python versions in documentation :gh:`898` - Raphael Nestler
* Align BSD-3 license with OSI template :gh:`912` - Lukas Kahwe Smith

Version 2.10.3
--------------

This is a bugfix release for Babel 2.10.2, which was mistakenly packaged with outdated locale data.

Thanks to Michał Górny for pointing this out and Jun Omae for verifying.

This and future Babel PyPI packages will be built by a more automated process,
which should make problems like this less likely to occur.

Version 2.10.2
--------------

This is a bugfix release for Babel 2.10.1.

* Fallback count="other" format in format_currency() (:gh:`872`) - Jun Omae
* Fix get_period_id() with ``dayPeriodRule`` across 0:00 (:gh:`871`) - Jun Omae
* Add support for ``b`` and ``B`` period symbols in time format (:gh:`869`) - Jun Omae
* chore(docs/typo): Fixes a minor typo in a function comment (:gh:`864`) - Frank Harrison

Version 2.10.1
--------------

This is a bugfix release for Babel 2.10.0.

* Messages: Fix ``distutils`` import. Regressed in :gh:`843`. (:gh:`852`) - Nehal J Wani
* The wheel file is no longer marked as universal, since Babel only supports Python 3.

Version 2.10.0
--------------

Upcoming deprecation
~~~~~~~~~~~~~~~~~~~~

* The ``get_next_timezone_transition()`` function is marked deprecated in this version and will be removed
  likely as soon as Babel 2.11.  No replacement for this function is planned; based on discussion in
  :gh:`716`, it's likely the function is not used in any real code. (:gh:`852`) - Aarni Koskela, Paul Ganssle

Improvements
~~~~~~~~~~~~

* CLDR: Upgrade to CLDR 41.0. (:gh:`853`) - Aarni Koskela

   * The ``c`` and ``e`` plural form operands introduced in CLDR 40 are parsed, but otherwise unsupported. (:gh:`826`)
   * Non-nominative forms of units are currently ignored.

* Messages: Implement ``--init-missing`` option for ``pybabel update`` (:gh:`785`) - ruro
* Messages: For ``extract``, you can now replace the built-in ``.*`` / ``_*`` ignored directory patterns
  with ones of your own. (:gh:`832`) - Aarni Koskela, Kinshuk Dua
* Messages: Add ``--check`` to verify if catalogs are up-to-date (:gh:`831`) - Krzysztof Jagiełło
* Messages: Add ``--header-comment`` to override default header comment (:gh:`720`) - Mohamed Hafez Morsy, Aarni Koskela
* Dates: ``parse_time`` now supports 12-hour clock, and is better at parsing partial times.
  (:gh:`834`) - Aarni Koskela, David Bauer, Arthur Jovart
* Dates: ``parse_date`` and ``parse_time`` now raise ``ParseError``, a subclass of ``ValueError``, in certain cases.
  (:gh:`834`) - Aarni Koskela
* Dates: ``parse_date`` and ``parse_time`` now accept the ``format`` parameter.
  (:gh:`834`) - Juliette Monsel, Aarni Koskela

Infrastructure
~~~~~~~~~~~~~~

* The internal ``babel/_compat.py`` module is no more (:gh:`808`) - Hugo van Kemenade
* Python 3.10 is officially supported (:gh:`809`) - Hugo van Kemenade
* There's now a friendly GitHub issue template. (:gh:`800`) – Álvaro Mondéjar Rubio
* Don't use the deprecated format_number function internally or in tests - Aarni Koskela
* Add GitHub URL for PyPi (:gh:`846`) - Andrii Oriekhov
* Python 3.12 compatibility: Prefer setuptools imports to distutils imports (:gh:`843`) - Aarni Koskela
* Python 3.11 compatibility: Add deprecations to l*gettext variants (:gh:`835`) - Aarni Koskela
* CI: Babel is now tested with PyPy 3.7. (:gh:`851`) - Aarni Koskela

Bugfixes
~~~~~~~~

* Date formatting: Allow using ``other`` as fallback form (:gh:`827`) - Aarni Koskela
* Locales: ``Locale.parse()`` normalizes variant tags to upper case (:gh:`829`) - Aarni Koskela
* A typo in the plural format for Maltese is fixed. (:gh:`796`) - Lukas Winkler
* Messages: Catalog date parsing is now timezone independent. (:gh:`701`) - rachele-collin
* Messages: Fix duplicate locations when writing without lineno (:gh:`837`) - Sigurd Ljødal
* Messages: Fix missing trailing semicolon in plural form headers (:gh:`848`) - farhan5900
* CLI: Fix output of ``--list-locales`` to not be a bytes repr (:gh:`845`) - Morgan Wahl

Documentation
~~~~~~~~~~~~~

* Documentation is now correctly built again, and up to date (:gh:`830`) - Aarni Koskela


Version 2.9.1
-------------

Bugfixes
~~~~~~~~

* The internal locale-data loading functions now validate the name of the locale file to be loaded and only
  allow files within Babel's data directory.  Thank you to Chris Lyne of Tenable, Inc. for discovering the issue!

Version 2.9.0
-------------

Upcoming version support changes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* This version, Babel 2.9, is the last version of Babel to support Python 2.7, Python 3.4, and Python 3.5.

Improvements
~~~~~~~~~~~~

* CLDR: Use CLDR 37 – Aarni Koskela (:gh:`734`)
* Dates: Handle ZoneInfo objects in get_timezone_location, get_timezone_name - Alessio Bogon (:gh:`741`)
* Numbers: Add group_separator feature in number formatting - Abdullah Javed Nesar (:gh:`726`)

Bugfixes
~~~~~~~~

* Dates: Correct default Format().timedelta format to 'long' to mute deprecation warnings – Aarni Koskela
* Import: Simplify iteration code in "import_cldr.py" – Felix Schwarz
* Import: Stop using deprecated ElementTree methods "getchildren()" and "getiterator()" – Felix Schwarz
* Messages: Fix unicode printing error on Python 2 without TTY. – Niklas Hambüchen
* Messages: Introduce invariant that _invalid_pofile() takes unicode line. – Niklas Hambüchen
* Tests: fix tests when using Python 3.9 – Felix Schwarz
* Tests: Remove deprecated 'sudo: false' from Travis configuration – Jon Dufresne
* Tests: Support Py.test 6.x – Aarni Koskela
* Utilities: LazyProxy: Handle AttributeError in specified func – Nikiforov Konstantin (:gh:`724`)
* Utilities: Replace usage of parser.suite with ast.parse – Miro Hrončok

Documentation
~~~~~~~~~~~~~

* Update parse_number comments – Brad Martin (:gh:`708`)
* Add __iter__ to Catalog documentation – @CyanNani123

Version 2.8.1
-------------

This is solely a patch release to make running tests on Py.test 6+ possible.

Bugfixes
~~~~~~~~

* Support Py.test 6 - Aarni Koskela (:gh:`747`, :gh:`750`, :gh:`752`)

Version 2.8.0
-------------

Improvements
~~~~~~~~~~~~

* CLDR: Upgrade to CLDR 36.0 - Aarni Koskela (:gh:`679`)
* Messages: Don't even open files with the "ignore" extraction method - @sebleblanc (:gh:`678`)

Bugfixes
~~~~~~~~

* Numbers: Fix formatting very small decimals when quantization is disabled - Lev Lybin, @miluChen (:gh:`662`)
* Messages: Attempt to sort all messages – Mario Frasca (:gh:`651`, :gh:`606`)

Docs
~~~~

* Add years to changelog - Romuald Brunet
* Note that installation requires pytz - Steve (Gadget) Barnes

Version 2.7.0
-------------

Possibly incompatible changes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

These may be backward incompatible in some cases, as some more-or-less internal
APIs have changed. Please feel free to file issues if you bump into anything
strange and we'll try to help!

* General: Internal uses of ``babel.util.odict`` have been replaced with
  ``collections.OrderedDict`` from The Python standard library.

Improvements
~~~~~~~~~~~~

* CLDR: Upgrade to CLDR 35.1 - Alberto Mardegan, Aarni Koskela (:gh:`626`, :gh:`643`)
* General: allow anchoring path patterns to the start of a string - Brian Cappello (:gh:`600`)
* General: Bumped version requirement on pytz - @chrisbrake (:gh:`592`)
* Messages: `pybabel compile`: exit with code 1 if errors were encountered - Aarni Koskela (:gh:`647`)
* Messages: Add omit-header to update_catalog - Cédric Krier (:gh:`633`)
* Messages: Catalog update: keep user comments from destination by default - Aarni Koskela (:gh:`648`)
* Messages: Skip empty message when writing mo file - Cédric Krier (:gh:`564`)
* Messages: Small fixes to avoid crashes on badly formatted .po files - Bryn Truscott (:gh:`597`)
* Numbers: `parse_decimal()` `strict` argument and `suggestions` - Charly C (:gh:`590`)
* Numbers: don't repeat suggestions in parse_decimal strict - Serban Constantin (:gh:`599`)
* Numbers: implement currency formatting with long display names - Luke Plant (:gh:`585`)
* Numbers: parse_decimal(): assume spaces are equivalent to non-breaking spaces when not in strict mode - Aarni Koskela (:gh:`649`)
* Performance: Cache locale_identifiers() - Aarni Koskela (:gh:`644`)

Bugfixes
~~~~~~~~

* CLDR: Skip alt=... for week data (minDays, firstDay, weekendStart, weekendEnd) - Aarni Koskela (:gh:`634`)
* Dates: Fix wrong weeknumber for 31.12.2018 - BT-sschmid (:gh:`621`)
* Locale: Avoid KeyError trying to get data on WindowsXP - mondeja (:gh:`604`)
* Locale: get_display_name(): Don't attempt to concatenate variant information to None - Aarni Koskela (:gh:`645`)
* Messages: pofile: Add comparison operators to _NormalizedString - Aarni Koskela (:gh:`646`)
* Messages: pofile: don't crash when message.locations can't be sorted - Aarni Koskela (:gh:`646`)

Tooling & docs
~~~~~~~~~~~~~~

* Docs: Remove all references to deprecated easy_install - Jon Dufresne (:gh:`610`)
* Docs: Switch print statement in docs to print function - NotAFile
* Docs: Update all pypi.python.org URLs to pypi.org - Jon Dufresne (:gh:`587`)
* Docs: Use https URLs throughout project where available - Jon Dufresne (:gh:`588`)
* Support: Add testing and document support for Python 3.7 - Jon Dufresne (:gh:`611`)
* Support: Test on Python 3.8-dev - Aarni Koskela (:gh:`642`)
* Support: Using ABCs from collections instead of collections.abc is deprecated. - Julien Palard (:gh:`609`)
* Tests: Fix conftest.py compatibility with pytest 4.3 - Miro Hrončok (:gh:`635`)
* Tests: Update pytest and pytest-cov - Miro Hrončok (:gh:`635`)

Version 2.6.0
-------------

Possibly incompatible changes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

These may be backward incompatible in some cases, as some more-or-less internal APIs have changed.
Please feel free to file issues if you bump into anything strange and we'll try to help!

* Numbers: Refactor decimal handling code and allow bypass of decimal quantization. (@kdeldycke) (PR :gh:`538`)
* Messages: allow processing files that are in locales unknown to Babel (@akx) (PR :gh:`557`)
* General: Drop support for EOL Python 2.6 and 3.3 (@hugovk) (PR :gh:`546`)

Other changes
~~~~~~~~~~~~~

* CLDR: Use CLDR 33 (@akx) (PR :gh:`581`)
* Lists: Add support for various list styles other than the default (@akx) (:gh:`552`)
* Messages: Add new PoFileError exception (@Bedrock02) (PR :gh:`532`)
* Times: Simplify Linux distro specific explicit timezone setting search (@scop) (PR :gh:`528`)

Bugfixes
~~~~~~~~

* CLDR: avoid importing alt=narrow currency symbols (@akx) (PR :gh:`558`)
* CLDR: ignore non-Latin numbering systems (@akx) (PR :gh:`579`)
* Docs: Fix improper example for date formatting (@PTrottier) (PR :gh:`574`)
* Tooling: Fix some deprecation warnings (@akx) (PR :gh:`580`)

Tooling & docs
~~~~~~~~~~~~~~

* Add explicit signatures to some date autofunctions (@xmo-odoo) (PR :gh:`554`)
* Include license file in the generated wheel package (@jdufresne) (PR :gh:`539`)
* Python 3.6 invalid escape sequence deprecation fixes (@scop) (PR :gh:`528`)
* Test and document all supported Python versions (@jdufresne) (PR :gh:`540`)
* Update copyright header years and authors file (@akx) (PR :gh:`559`)


Version 2.5.3
-------------

This is a maintenance release that reverts undesired API-breaking changes that slipped into 2.5.2
(see :gh:`550`).

It is based on v2.5.1 (f29eccd) with commits 7cedb84, 29da2d2 and edfb518 cherry-picked on top.

Version 2.5.2
-------------

Bugfixes
~~~~~~~~

* Revert the unnecessary PyInstaller fixes from 2.5.0 and 2.5.1 (:gh:`533`) (@yagebu)

Version 2.5.1
-------------

Minor Improvements and bugfixes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Use a fixed datetime to avoid test failures (:gh:`520`) (@narendravardi)
* Parse multi-line __future__ imports better (:gh:`519`) (@akx)
* Fix validate_currency docstring (:gh:`522`)
* Allow normalize_locale and exists to handle various unexpected inputs (:gh:`523`) (@suhojm)
* Make PyInstaller support more robust (:gh:`525`, :gh:`526`) (@thijstriemstra, @akx)


Version 2.5.0
-------------

New Features
~~~~~~~~~~~~

* Numbers: Add currency utilities and helpers (:gh:`491`) (@kdeldycke)
* Support PyInstaller (:gh:`500`, :gh:`505`) (@wodo)

Minor Improvements and bugfixes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Dates: Add __str__ to DateTimePattern (:gh:`515`) (@sfermigier)
* Dates: Fix an invalid string to bytes comparison when parsing TZ files on Py3 (:gh:`498`) (@rowillia)
* Dates: Formatting zero-padded components of dates is faster (:gh:`517`) (@akx)
* Documentation: Fix "Good Commits" link in CONTRIBUTING.md (:gh:`511`) (@naryanacharya6)
* Documentation: Fix link to Python gettext module (:gh:`512`) (@Linkid)
* Messages: Allow both dash and underscore separated locale identifiers in pofiles (:gh:`489`, :gh:`490`) (@akx)
* Messages: Extract Python messages in nested gettext calls (:gh:`488`) (@sublee)
* Messages: Fix in-place editing of dir list while iterating (:gh:`476`, :gh:`492`) (@MarcDufresne)
* Messages: Stabilize sort order (:gh:`482`) (@xavfernandez)
* Time zones: Honor the no-inherit marker for metazone names (:gh:`405`) (@akx)


Version 2.4.0
-------------

New Features
~~~~~~~~~~~~

Some of these changes might break your current code and/or tests.

* CLDR: CLDR 29 is now used instead of CLDR 28 (:gh:`405`) (@akx)
* Messages: Add option 'add_location' for location line formatting (:gh:`438`, :gh:`459`) (@rrader, @alxpy)
* Numbers: Allow full control of decimal behavior (:gh:`410`) (@etanol)

Minor Improvements and bugfixes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Documentation: Improve Date Fields descriptions (:gh:`450`) (@ldwoolley)
* Documentation: Typo fixes and documentation improvements (:gh:`406`, :gh:`412`, :gh:`403`, :gh:`440`, :gh:`449`, :gh:`463`) (@zyegfryed, @adamchainz, @jwilk, @akx, @roramirez, @abhishekcs10)
* Messages: Default to UTF-8 source encoding instead of ISO-8859-1 (:gh:`399`) (@asottile)
* Messages: Ensure messages are extracted in the order they were passed in (:gh:`424`) (@ngrilly)
* Messages: Message extraction for JSX files is improved (:gh:`392`, :gh:`396`, :gh:`425`) (@karloskar, @georgschoelly)
* Messages: PO file reading supports multi-line obsolete units (:gh:`429`) (@mbirtwell)
* Messages: Python message extractor respects unicode_literals in __future__ (:gh:`427`) (@sublee)
* Messages: Roundtrip Language headers (:gh:`420`) (@kruton)
* Messages: units before obsolete units are no longer erroneously marked obsolete (:gh:`452`) (@mbirtwell)
* Numbers: `parse_pattern` now preserves the full original pattern (:gh:`414`) (@jtwang)
* Numbers: Fix float conversion in `extract_operands` (:gh:`435`) (@akx)
* Plurals: Fix plural forms for Czech and Slovak locales (:gh:`373`) (@ykshatroff)
* Plurals: More plural form fixes based on Mozilla and CLDR references (:gh:`431`) (@mshenfield)


Internal improvements
~~~~~~~~~~~~~~~~~~~~~

* Local times are constructed correctly in tests (:gh:`411`) (@etanol)
* Miscellaneous small improvements (:gh:`437`) (@scop)
* Regex flags are extracted from the regex strings (:gh:`462`) (@singingwolfboy)
* The PO file reader is now a class and has seen some refactoring (:gh:`429`, :gh:`452`) (@mbirtwell)


Version 2.3.4
-------------

(Bugfix release, released on April 22th 2016)

Bugfixes
~~~~~~~~

* CLDR: The lxml library is no longer used for CLDR importing, so it should not cause strange failures either. Thanks to @aronbierbaum for the bug report and @jtwang for the fix. (:gh:`393`)
* CLI: Every last single CLI usage regression should now be gone, and both distutils and stand-alone CLIs should work as they have in the past. Thanks to @paxswill and @ajaeger for bug reports. (:gh:`389`)

Version 2.3.3
-------------

(Bugfix release, released on April 12th 2016)

Bugfixes
~~~~~~~~

* CLI: Usage regressions that had snuck in between 2.2 and 2.3 should be no more. (:gh:`386`) Thanks to @ajaeger, @sebdiem and @jcristovao for bug reports and patches.

Version 2.3.2
-------------

(Bugfix release, released on April 9th 2016)

Bugfixes
~~~~~~~~

* Dates: Period (am/pm) formatting was broken in certain locales (namely zh_TW). Thanks to @jun66j5 for the bug report. (:gh:`378`, :gh:`379`)

Version 2.3.1
-------------

(Bugfix release because of deployment problems, released on April 8th 2016)

Version 2.3
-----------

(Feature release, released on April 8th 2016)

Internal improvements
~~~~~~~~~~~~~~~~~~~~~

* The CLI frontend and Distutils commands use a shared implementation (:gh:`311`)
* PyPy3 is supported (:gh:`343`)

Features
~~~~~~~~

* CLDR: Add an API for territory language data (:gh:`315`)
* Core: Character order and measurement system data is imported and exposed (:gh:`368`)
* Dates: Add an API for time interval formatting (:gh:`316`)
* Dates: More pattern formats and lengths are supported (:gh:`347`)
* Dates: Period IDs are imported and exposed (:gh:`349`)
* Dates: Support for date-time skeleton formats has been added (:gh:`265`)
* Dates: Timezone formatting has been improved (:gh:`338`)
* Messages: JavaScript extraction now supports dotted names, ES6 template strings and JSX tags (:gh:`332`)
* Messages: npgettext is recognized by default (:gh:`341`)
* Messages: The CLI learned to accept multiple domains (:gh:`335`)
* Messages: The extraction commands now accept filenames in addition to directories (:gh:`324`)
* Units: A new API for unit formatting is implemented (:gh:`369`)

Bugfixes
~~~~~~~~

* Core: Mixed-case locale IDs work more reliably (:gh:`361`)
* Dates: S...S formats work correctly now (:gh:`360`)
* Messages: All messages are now sorted correctly if sorting has been specified (:gh:`300`)
* Messages: Fix the unexpected behavior caused by catalog header updating (e0e7ef1) (:gh:`320`)
* Messages: Gettext operands are now generated correctly (:gh:`295`)
* Messages: Message extraction has been taught to detect encodings better (:gh:`274`)

Version 2.2
-----------

(Feature release, released on January 2nd 2016)

Bugfixes
~~~~~~~~

* General: Add __hash__ to Locale. (:gh:`303`) (2aa8074)
* General: Allow files with BOM if they're UTF-8 (:gh:`189`) (da87edd)
* General: localedata directory is now locale-data (:gh:`109`) (2d1882e)
* General: odict: Fix pop method (0a9e97e)
* General: Removed uses of datetime.date class from .dat files (:gh:`174`) (94f6830)
* Messages: Fix plural selection for Chinese (531f666)
* Messages: Fix typo and add semicolon in plural_forms (5784501)
* Messages: Flatten NullTranslations.files into a list (ad11101)
* Times: FixedOffsetTimezone: fix display of negative offsets (d816803)

Features
~~~~~~~~

* CLDR: Update to CLDR 28 (:gh:`292`) (9f7f4d0)
* General: Add __copy__ and __deepcopy__ to LazyProxy. (a1cc3f1)
* General: Add official support for Python 3.4 and 3.5
* General: Improve odict performance by making key search O(1) (6822b7f)
* Locale: Add an ordinal_form property to Locale (:gh:`270`) (b3f3430)
* Locale: Add support for list formatting (37ce4fa, be6e23d)
* Locale: Check inheritance exceptions first (3ef0d6d)
* Messages: Allow file locations without line numbers (:gh:`279`) (79bc781)
* Messages: Allow passing a callable to `extract()` (:gh:`289`) (3f58516)
* Messages: Support 'Language' header field of PO files (:gh:`76`) (3ce842b)
* Messages: Update catalog headers from templates (e0e7ef1)
* Numbers: Properly load and expose currency format types (:gh:`201`) (df676ab)
* Numbers: Use cdecimal by default when available (b6169be)
* Numbers: Use the CLDR's suggested number of decimals for format_currency (:gh:`139`) (201ed50)
* Times: Add format_timedelta(format='narrow') support (edc5eb5)

Version 2.1
-----------

(Bugfix/minor feature release, released on September 25th 2015)

- Parse and honour the locale inheritance exceptions
  (:gh:`97`)
- Fix Locale.parse using ``global.dat`` incompatible types
  (:gh:`174`)
- Fix display of negative offsets in ``FixedOffsetTimezone``
  (:gh:`214`)
- Improved odict performance which is used during localization file
  build, should improve compilation time for large projects
- Add support for "narrow" format for ``format_timedelta``
- Add universal wheel support
- Support 'Language' header field in .PO files
  (fixes :gh:`76`)
- Test suite enhancements (coverage, broken tests fixed, etc)
- Documentation updated

Version 2.0
-----------

(Released on July 27th 2015, codename Second Coming)

- Added support for looking up currencies that belong to a territory
  through the :func:`babel.numbers.get_territory_currencies`
  function.
- Improved Python 3 support.
- Fixed some broken tests for timezone behavior.
- Improved various smaller things for dealing with dates.

Version 1.4
-----------

(bugfix release, release date to be decided)

- Fixed a bug that caused deprecated territory codes not being
  converted properly by the subtag resolving.  This for instance
  showed up when trying to use ``und_UK`` as a language code
  which now properly resolves to ``en_GB``.
- Fixed a bug that made it impossible to import the CLDR data
  from scratch on windows systems.

Version 1.3
-----------

(bugfix release, released on July 29th 2013)

- Fixed a bug in likely-subtag resolving for some common locales.
  This primarily makes ``zh_CN`` work again which was broken
  due to how it was defined in the likely subtags combined with
  our broken resolving.  This fixes :gh:`37`.
- Fixed a bug that caused pybabel to break when writing to stdout
  on Python 3.
- Removed a stray print that was causing issues when writing to
  stdout for message catalogs.

Version 1.2
-----------

(bugfix release, released on July 27th 2013)

- Included all tests in the tarball.  Previously the include
  skipped past recursive folders.
- Changed how tests are invoked and added separate standalone
  test command.  This simplifies testing of the package for
  linux distributors.

Version 1.1
-----------

(bugfix release, released on July 27th 2013)

- added dummy version requirements for pytz so that it installs
  on pip 1.4.
- Included tests in the tarball.

Version 1.0
-----------

(Released on July 26th 2013, codename Revival)

- support python 2.6, 2.7, 3.3+ and pypy - drop all other versions
- use tox for testing on different pythons
- Added support for the locale plural rules defined by the CLDR.
- Added `format_timedelta` function to support localized formatting of
  relative times with strings such as "2 days" or "1 month" (:trac:`126`).
- Fixed negative offset handling of Catalog._set_mime_headers (:trac:`165`).
- Fixed the case where messages containing square brackets would break with
  an unpack error.
- updated to CLDR 23
- Make the CLDR import script work with Python 2.7.
- Fix various typos.
- Sort output of list-locales.
- Make the POT-Creation-Date of the catalog being updated equal to
  POT-Creation-Date of the template used to update (:trac:`148`).
- Use a more explicit error message if no option or argument (command) is
  passed to pybabel (:trac:`81`).
- Keep the PO-Revision-Date if it is not the default value (:trac:`148`).
- Make --no-wrap work by reworking --width's default and mimic xgettext's
  behaviour of always wrapping comments (:trac:`145`).
- Add --project and --version options for commandline (:trac:`173`).
- Add a __ne__() method to the Local class.
- Explicitly sort instead of using sorted() and don't assume ordering
  (Jython compatibility).
- Removed ValueError raising for string formatting message checkers if the
  string does not contain any string formatting (:trac:`150`).
- Fix Serbian plural forms (:trac:`213`).
- Small speed improvement in format_date() (:trac:`216`).
- Fix so frontend.CommandLineInterface.run does not accumulate logging
  handlers (:trac:`227`, reported with initial patch by dfraser)
- Fix exception if environment contains an invalid locale setting
  (:trac:`200`)
- use cPickle instead of pickle for better performance (:trac:`225`)
- Only use bankers round algorithm as a tie breaker if there are two nearest
  numbers, round as usual if there is only one nearest number (:trac:`267`,
  patch by Martin)
- Allow disabling cache behaviour in LazyProxy (:trac:`208`, initial patch
  from Pedro Algarvio)
- Support for context-aware methods during message extraction (:trac:`229`,
  patch from David Rios)
- "init" and "update" commands support "--no-wrap" option (:trac:`289`)
- fix formatting of fraction in format_decimal() if the input value is a float
  with more than 7 significant digits (:trac:`183`)
- fix format_date() with datetime parameter (:trac:`282`, patch from Xavier
  Morel)
- fix format_decimal() with small Decimal values (:trac:`214`, patch from
  George Lund)
- fix handling of messages containing '\\n' (:trac:`198`)
- handle irregular multi-line msgstr (no "" as first line) gracefully
  (:trac:`171`)
- parse_decimal() now returns Decimals not floats, API change (:trac:`178`)
- no warnings when running setup.py without installed setuptools (:trac:`262`)
- modified Locale.__eq__ method so Locales are only equal if all of their
  attributes (language, territory, script, variant) are equal
- resort to hard-coded message extractors/checkers if pkg_resources is
  installed but no egg-info was found (:trac:`230`)
- format_time() and format_datetime() now accept also floats (:trac:`242`)
- add babel.support.NullTranslations class similar to gettext.NullTranslations
  but with all of Babel's new gettext methods (:trac:`277`)
- "init" and "update" commands support "--width" option (:trac:`284`)
- fix 'input_dirs' option for setuptools integration (:trac:`232`, initial
  patch by Étienne Bersac)
- ensure .mo file header contains the same information as the source .po file
  (:trac:`199`)
- added support for get_language_name() on the locale objects.
- added support for get_territory_name() on the locale objects.
- added support for get_script_name() on the locale objects.
- added pluralization support for currency names and added a '¤¤¤'
  pattern for currencies that includes the full name.
- depend on pytz now and wrap it nicer.  This gives us improved support
  for things like timezone transitions and an overall nicer API.
- Added support for explicit charset to PO file reading.
- Added experimental Python 3 support.
- Added better support for returning timezone names.
- Don't throw away a Catalog's obsolete messages when updating it.
- Added basic likelySubtag resolving when doing locale parsing and no
  match can be found.


Version 0.9.6
-------------

(released on March 17th 2011)

- Backport r493-494: documentation typo fixes.
- Make the CLDR import script work with Python 2.7.
- Fix various typos.
- Fixed Python 2.3 compatibility (:trac:`146`, :trac:`233`).
- Sort output of list-locales.
- Make the POT-Creation-Date of the catalog being updated equal to
  POT-Creation-Date of the template used to update (:trac:`148`).
- Use a more explicit error message if no option or argument (command) is
  passed to pybabel (:trac:`81`).
- Keep the PO-Revision-Date if it is not the default value (:trac:`148`).
- Make --no-wrap work by reworking --width's default and mimic xgettext's
  behaviour of always wrapping comments (:trac:`145`).
- Fixed negative offset handling of Catalog._set_mime_headers (:trac:`165`).
- Add --project and --version options for commandline (:trac:`173`).
- Add a __ne__() method to the Local class.
- Explicitly sort instead of using sorted() and don't assume ordering
  (Python 2.3 and Jython compatibility).
- Removed ValueError raising for string formatting message checkers if the
  string does not contain any string formatting (:trac:`150`).
- Fix Serbian plural forms (:trac:`213`).
- Small speed improvement in format_date() (:trac:`216`).
- Fix number formatting for locales where CLDR specifies alt or draft
  items (:trac:`217`)
- Fix bad check in format_time (:trac:`257`, reported with patch and tests by
  jomae)
- Fix so frontend.CommandLineInterface.run does not accumulate logging
  handlers (:trac:`227`, reported with initial patch by dfraser)
- Fix exception if environment contains an invalid locale setting
  (:trac:`200`)


Version 0.9.5
-------------

(released on April 6th 2010)

- Fixed the case where messages containing square brackets would break with
  an unpack error.
- Backport of r467: Fuzzy matching regarding plurals should *NOT* be checked
  against len(message.id)  because this is always 2, instead, it's should be
  checked against catalog.num_plurals (:trac:`212`).


Version 0.9.4
-------------

(released on August 25th 2008)

- Currency symbol definitions that is defined with choice patterns in the
  CLDR data are no longer imported, so the symbol code will be used instead.
- Fixed quarter support in date formatting.
- Fixed a serious memory leak that was introduces by the support for CLDR
  aliases in 0.9.3 (:trac:`128`).
- Locale modifiers such as "@euro" are now stripped from locale identifiers
  when parsing (:trac:`136`).
- The system locales "C" and "POSIX" are now treated as aliases for
  "en_US_POSIX", for which the CLDR provides the appropriate data. Thanks to
  Manlio Perillo for the suggestion.
- Fixed JavaScript extraction for regular expression literals (:trac:`138`)
  and concatenated strings.
- The `Translation` class in `babel.support` can now manage catalogs with
  different message domains, and exposes the family of `d*gettext` functions
  (:trac:`137`).


Version 0.9.3
-------------

(released on July 9th 2008)

- Fixed invalid message extraction methods causing an UnboundLocalError.
- Extraction method specification can now use a dot instead of the colon to
  separate module and function name (:trac:`105`).
- Fixed message catalog compilation for locales with more than two plural
  forms (:trac:`95`).
- Fixed compilation of message catalogs for locales with more than two plural
  forms where the translations were empty (:trac:`97`).
- The stripping of the comment tags in comments is optional now and
  is done for each line in a comment.
- Added a JavaScript message extractor.
- Updated to CLDR 1.6.
- Fixed timezone calculations when formatting datetime and time values.
- Added a `get_plural` function into the plurals module that returns the
  correct plural forms for a locale as tuple.
- Added support for alias definitions in the CLDR data files, meaning that
  the chance for items missing in certain locales should be greatly reduced
  (:trac:`68`).


Version 0.9.2
-------------

(released on February 4th 2008)

- Fixed catalogs' charset values not being recognized (:trac:`66`).
- Numerous improvements to the default plural forms.
- Fixed fuzzy matching when updating message catalogs (:trac:`82`).
- Fixed bug in catalog updating, that in some cases pulled in translations
  from different catalogs based on the same template.
- Location lines in PO files do no longer get wrapped at hyphens in file
  names (:trac:`79`).
- Fixed division by zero error in catalog compilation on empty catalogs
  (:trac:`60`).


Version 0.9.1
-------------

(released on September 7th 2007)

- Fixed catalog updating when a message is merged that was previously simple
  but now has a plural form, for example by moving from `gettext` to
  `ngettext`, or vice versa.
- Fixed time formatting for 12 am and 12 pm.
- Fixed output encoding of the `pybabel --list-locales` command.
- MO files are now written in binary mode on windows (:trac:`61`).


Version 0.9
-----------

(released on August 20th 2007)

- The `new_catalog` distutils command has been renamed to `init_catalog` for
  consistency with the command-line frontend.
- Added compilation of message catalogs to MO files (:trac:`21`).
- Added updating of message catalogs from POT files (:trac:`22`).
- Support for significant digits in number formatting.
- Apply proper "banker's rounding" in number formatting in a cross-platform
  manner.
- The number formatting functions now also work with numbers represented by
  Python `Decimal` objects (:trac:`53`).
- Added extensible infrastructure for validating translation catalogs.
- Fixed the extractor not filtering out messages that didn't validate against
  the keyword's specification (:trac:`39`).
- Fixed the extractor raising an exception when encountering an empty string
  msgid. It now emits a warning to stderr.
- Numerous Python message extractor fixes: it now handles nested function
  calls within a gettext function call correctly, uses the correct line number
  for multi-line function calls, and other small fixes (tickets :trac:`38` and
  :trac:`39`).
- Improved support for detecting Python string formatting fields in message
  strings (:trac:`57`).
- CLDR upgraded to the 1.5 release.
- Improved timezone formatting.
- Implemented scientific number formatting.
- Added mechanism to lookup locales by alias, for cases where browsers insist
  on including only the language code in the `Accept-Language` header, and
  sometimes even the incorrect language code.


Version 0.8.1
-------------

(released on July 2nd 2007)

- `default_locale()` would fail when the value of the `LANGUAGE` environment
  variable contained multiple language codes separated by colon, as is
  explicitly allowed by the GNU gettext tools. As the `default_locale()`
  function is called at the module level in some modules, this bug would
  completely break importing these modules on systems where `LANGUAGE` is set
  that way.
- The character set specified in PO template files is now respected when
  creating new catalog files based on that template. This allows the use of
  characters outside the ASCII range in POT files (:trac:`17`).
- The default ordering of messages in generated POT files, which is based on
  the order those messages are found when walking the source tree, is no
  longer subject to differences between platforms; directory and file names
  are now always sorted alphabetically.
- The Python message extractor now respects the special encoding comment to be
  able to handle files containing non-ASCII characters (:trac:`23`).
- Added ``N_`` (gettext noop) to the extractor's default keywords.
- Made locale string parsing more robust, and also take the script part into
  account (:trac:`27`).
- Added a function to list all locales for which locale data is available.
- Added a command-line option to the `pybabel` command which prints out all
  available locales (:trac:`24`).
- The name of the command-line script has been changed from just `babel` to
  `pybabel` to avoid a conflict with the OpenBabel project (:trac:`34`).


Version 0.8
-----------

(released on June 20th 2007)

- First public release
