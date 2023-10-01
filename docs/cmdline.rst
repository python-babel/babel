.. -*- mode: rst; encoding: utf-8 -*-

.. _cmdline:

======================
Command-Line Interface
======================

Babel includes a command-line interface for working with message catalogs,
similar to the various GNU ``gettext`` tools commonly available on Linux/Unix
systems.


When properly installed, Babel provides a script called ``pybabel``::

    $ pybabel --help
    Usage: pybabel command [options] [args]

    Options:
      --version       show program's version number and exit
      -h, --help      show this help message and exit
      --list-locales  print all known locales and exit
      -v, --verbose   print as much as possible
      -q, --quiet     print as little as possible

    commands:
      compile  compile message catalogs to MO files
      extract  extract messages from source files and generate a POT file
      init     create new message catalogs from a POT file
      update   update existing message catalogs from a POT file

The ``pybabel`` script provides a number of sub-commands that do the actual
work. Those sub-commands are described below.


compile
=======

The ``compile`` sub-command can be used to compile translation catalogs into
binary MO files::

    $ pybabel compile --help
    Usage: pybabel compile [options]

    compile message catalogs to MO files

    Options:
      -h, --help            show this help message and exit
      -D DOMAIN, --domain=DOMAIN
                            domains of PO files (space separated list, default
                            'messages')
      -d DIRECTORY, --directory=DIRECTORY
                            path to base directory containing the catalogs
      -i INPUT_FILE, --input-file=INPUT_FILE
                            name of the input file
      -o OUTPUT_FILE, --output-file=OUTPUT_FILE
                            name of the output file (default
                            '<output_dir>/<locale>/LC_MESSAGES/<domain>.mo')
      -l LOCALE, --locale=LOCALE
                            locale of the catalog to compile
      -f, --use-fuzzy       also include fuzzy translations
      --statistics          print statistics about translations

If ``directory`` is specified, but ``output-file`` is not, the default filename
of the output file will be::

    <directory>/<locale>/LC_MESSAGES/<domain>.mo

If neither the ``input_file`` nor the ``locale`` option is set, this command
looks for all catalog files in the base directory that match the given domain,
and compiles each of them to MO files in the same directory.


extract
=======

The ``extract`` sub-command can be used to extract localizable messages from
a collection of source files::

    $ pybabel extract --help
    Usage: pybabel extract [options] <input-paths>

    extract messages from source files and generate a POT file

    Options:
      -h, --help            show this help message and exit
      --charset=CHARSET     charset to use in the output file (default "utf-8")
      -k KEYWORDS, --keywords=KEYWORDS, --keyword=KEYWORDS
                            space-separated list of keywords to look for in
                            addition to the defaults (may be repeated multiple
                            times)
      --no-default-keywords
                            do not include the default keywords
      -F MAPPING_FILE, --mapping-file=MAPPING_FILE, --mapping=MAPPING_FILE
                            path to the mapping configuration file
      --no-location         do not include location comments with filename and
                            line number
      --add-location=ADD_LOCATION
                            location lines format. If it is not given or "full",
                            it generates the lines with both file name and line
                            number. If it is "file", the line number part is
                            omitted. If it is "never", it completely suppresses
                            the lines (same as --no-location).
      --omit-header         do not include msgid "" entry in header
      -o OUTPUT_FILE, --output-file=OUTPUT_FILE, --output=OUTPUT_FILE
                            name of the output file
      -w WIDTH, --width=WIDTH
                            set output line width (default 76)
      --no-wrap             do not break long message lines, longer than the
                            output line width, into several lines
      --sort-output         generate sorted output (default False)
      --sort-by-file        sort output by file location (default False)
      --msgid-bugs-address=MSGID_BUGS_ADDRESS
                            set report address for msgid
      --copyright-holder=COPYRIGHT_HOLDER
                            set copyright holder in output
      --project=PROJECT     set project name in output
      --version=VERSION     set project version in output
      -c ADD_COMMENTS, --add-comments=ADD_COMMENTS
                            place comment block with TAG (or those preceding
                            keyword lines) in output file. Separate multiple TAGs
                            with commas(,)
      -s, --strip-comments, --strip-comment-tags
                            strip the comment TAGs from the comments.
      --input-dirs=INPUT_DIRS
                            alias for input-paths (does allow files as well as
                            directories).
      --ignore-dirs=IGNORE_DIRS
                            Patterns for directories to ignore when scanning for
                            messages. Separate multiple patterns with spaces
                            (default ".* ._")
      --header-comment=HEADER_COMMENT
                            header comment for the catalog


The meaning of ``--keyword`` values is as follows:

- Pass a simple identifier like ``_`` to extract the first (and only the first)
  argument of all function calls to ``_``,

- To extract other arguments than the first, add a colon and the argument
  indices separated by commas. For example, the ``dngettext`` function
  typically expects translatable strings as second and third arguments,
  so you could pass ``dngettext:2,3``.

- Some arguments should not be interpreted as translatable strings, but
  context strings. For that, append "c" to the argument index. For example:
  ``pgettext:1c,2``.

- In C++ and Python, you may have functions that behave differently
  depending on how many arguments they take. For this use case, you can
  add an integer followed by "t" after the colon. In this case, the
  keyword will only match a function invocation if it has the specified
  total number of arguments.  For example, if you have a function
  ``foo`` that behaves as ``gettext`` (argument is a message) or
  ``pgettext`` (arguments are a context and a message) depending on
  whether it takes one or two arguments, you can pass
  ``--keyword=foo:1,1t --keyword=foo:1c,2,2t``.

The default keywords are equivalent to passing ::

  --keyword=_
  --keyword=gettext
  --keyword=ngettext:1,2
  --keyword=ugettext
  --keyword=ungettext:1,2
  --keyword=dgettext:2
  --keyword=dngettext:2,3
  --keyword=N_
  --keyword=pgettext:1c,2
  --keyword=npgettext:1c,2,3



init
====

The `init` sub-command creates a new translations catalog based on a PO
template file::

    $ pybabel init --help
    Usage: pybabel init [options]

    create new message catalogs from a POT file

    Options:
      -h, --help            show this help message and exit
      -D DOMAIN, --domain=DOMAIN
                            domain of PO file (default 'messages')
      -i INPUT_FILE, --input-file=INPUT_FILE
                            name of the input file
      -d OUTPUT_DIR, --output-dir=OUTPUT_DIR
                            path to output directory
      -o OUTPUT_FILE, --output-file=OUTPUT_FILE
                            name of the output file (default
                            '<output_dir>/<locale>/LC_MESSAGES/<domain>.po')
      -l LOCALE, --locale=LOCALE
                            locale for the new localized catalog
      -w WIDTH, --width=WIDTH
                            set output line width (default 76)
      --no-wrap             do not break long message lines, longer than the
                            output line width, into several lines

update
======

The `update` sub-command updates an existing new translations catalog based on
a PO template file::

    $ pybabel update --help
    Usage: pybabel update [options]

    update existing message catalogs from a POT file

    Options:
      -h, --help            show this help message and exit
      -D DOMAIN, --domain=DOMAIN
                            domain of PO file (default 'messages')
      -i INPUT_FILE, --input-file=INPUT_FILE
                            name of the input file
      -d OUTPUT_DIR, --output-dir=OUTPUT_DIR
                            path to base directory containing the catalogs
      -o OUTPUT_FILE, --output-file=OUTPUT_FILE
                            name of the output file (default
                            '<output_dir>/<locale>/LC_MESSAGES/<domain>.po')
      --omit-header         do not include msgid  entry in header
      -l LOCALE, --locale=LOCALE
                            locale of the catalog to compile
      -w WIDTH, --width=WIDTH
                            set output line width (default 76)
      --no-wrap             do not break long message lines, longer than the
                            output line width, into several lines
      --ignore-obsolete     whether to omit obsolete messages from the output
      --init-missing        if any output files are missing, initialize them first
      -N, --no-fuzzy-matching
                            do not use fuzzy matching
      --update-header-comment
                            update target header comment
      --previous            keep previous msgids of translated messages


If ``output_dir`` is specified, but ``output-file`` is not, the default
filename of the output file will be::

    <directory>/<locale>/LC_MESSAGES/<domain>.mo

If neither the ``output_file`` nor the ``locale`` option is set, this command
looks for all catalog files in the base directory that match the given domain,
and updates each of them.
