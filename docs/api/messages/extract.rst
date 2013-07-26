Low-Level Extraction Interface
==============================

.. module:: babel.messages.extract

The low level extraction interface can be used to extract from directories
or files directly.  Normally this is not needed as the command line tools
can do that for you.

Extraction Functions
--------------------

The extraction functions are what the command line tools use internally to
extract strings.

.. autofunction:: extract_from_dir

.. autofunction:: extract_from_file

.. autofunction:: extract

Language Parsing
----------------

The language parsing functions are used to extract strings out of source
files.  These are automatically being used by the extraction functions but
sometimes it can be useful to register wrapper functions, then these low
level functions can be invoked.

New functions can be registered through the setuptools entrypoint system.

.. autofunction:: extract_python

.. autofunction:: extract_javascript

.. autofunction:: extract_nothing
