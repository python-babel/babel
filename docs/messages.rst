.. -*- mode: rst; encoding: utf-8 -*-

.. _messages:

=============================
Working with Message Catalogs
=============================


Introduction
============

The ``gettext`` translation system enables you to mark any strings used in your
application as subject to localization, by wrapping them in functions such as
``gettext(str)`` and ``ngettext(singular, plural, num)``. For brevity, the
``gettext`` function is often aliased to ``_(str)``, so you can write:

.. code-block:: python

    print(_("Hello"))

instead of just:

.. code-block:: python

    print("Hello")

to make the string "Hello" localizable.

Message catalogs are collections of translations for such localizable messages
used in an application. They are commonly stored in PO (Portable Object) and MO
(Machine Object) files, the formats of which are defined by the GNU `gettext`_
tools and the GNU `translation project`_.

 .. _`gettext`: https://www.gnu.org/software/gettext/
 .. _`translation project`: https://sourceforge.net/projects/translation/

The general procedure for building message catalogs looks something like this:

 * use a tool (such as ``xgettext``) to extract localizable strings from the
   code base and write them to a POT (PO Template) file.
 * make a copy of the POT file for a specific locale (for example, "en_US")
   and start translating the messages
 * use a tool such as ``msgfmt`` to compile the locale PO file into a binary
   MO file
 * later, when code changes make it necessary to update the translations, you
   regenerate the POT file and merge the changes into the various
   locale-specific PO files, for example using ``msgmerge``

Python provides the :mod:`gettext` module as part of the standard library,
which enables applications to work with appropriately generated MO files.

As ``gettext`` provides a solid and well supported foundation for translating
application messages, Babel does not reinvent the wheel, but rather reuses this
infrastructure, and makes it easier to build message catalogs for Python
applications.


Message Extraction
==================

Babel provides functionality similar to that of the ``xgettext`` program,
except that only extraction from Python source files is built-in, while support
for other file formats can be added using a simple extension mechanism.

Unlike ``xgettext``, which is usually invoked once for every file, the routines
for message extraction in Babel operate on directories. While the per-file
approach of ``xgettext`` works nicely with projects using a ``Makefile``,
Python projects rarely use ``make``, and thus a different mechanism is needed
for extracting messages from the heterogeneous collection of source files that
many Python projects are composed of.

When message extraction is based on directories instead of individual files,
there needs to be a way to configure which files should be treated in which
manner. For example, while many projects may contain ``.html`` files, some of
those files may be static HTML files that don't contain localizable message,
while others may be `Jinja2`_ templates, and still others may contain `Genshi`_
markup templates. Some projects may even mix HTML files for different templates
languages (for whatever reason). Therefore the way in which messages are
extracted from source files can not only depend on the file extension, but
needs to be controllable in a precise manner.

.. _`Jinja2`: https://jinja.pocoo.org/
.. _`Genshi`: https://genshi.edgewall.org/

Babel accepts a configuration file to specify this mapping of files to
extraction methods, which is described below.


.. _`frontends`:

----------
Front-Ends
----------

Babel provides two different front-ends to access its functionality for working
with message catalogs:

 * A :ref:`cmdline`, and
 * :ref:`setup-integration`

Which one you choose depends on the nature of your project. For most modern
Python projects, the distutils/setuptools integration is probably more
convenient.


.. _`mapping`:

-------------------------------------------
Extraction Method Mapping and Configuration
-------------------------------------------

The mapping of extraction methods to files in Babel is done via a configuration
file. This file maps extended glob patterns to the names of the extraction
methods, and can also set various options for each pattern (which options are
available depends on the specific extraction method).

For example, the following configuration adds extraction of messages from both
Genshi markup templates and text templates:

.. code-block:: ini

    # Extraction from Python source files

    [python: **.py]

    # Extraction from Genshi HTML and text templates

    [genshi: **/templates/**.html]
    ignore_tags = script,style
    include_attrs = alt title summary

    [genshi: **/templates/**.txt]
    template_class = genshi.template:TextTemplate
    encoding = ISO-8819-15

    # Extraction from JavaScript files

    [javascript: **.js]
    extract_messages = $._, jQuery._

The configuration file syntax is based on the format commonly found in ``.INI``
files on Windows systems, and as supported by the ``ConfigParser`` module in
the Python standard library. Section names (the strings enclosed in square
brackets) specify both the name of the extraction method, and the extended glob
pattern to specify the files that this extraction method should be used for,
separated by a colon. The options in the sections are passed to the extraction
method. Which options are available is specific to the extraction method used.

The extended glob patterns used in this configuration are similar to the glob
patterns provided by most shells. A single asterisk (``*``) is a wildcard for
any number of characters (except for the pathname component separator "/"),
while a question mark (``?``) only matches a single character. In addition,
two subsequent asterisk characters (``**``) can be used to make the wildcard
match any directory level, so the pattern ``**.txt`` matches any file with the
extension ``.txt`` in any directory.

Lines that start with a ``#`` or ``;`` character are ignored and can be used
for comments. Empty lines are ignored, too.

.. note:: if you're performing message extraction using the command Babel
          provides for integration into ``setup.py`` scripts, you can also
          provide this configuration in a different way, namely as a keyword
          argument to the ``setup()`` function. See
          :ref:`setup-integration` for more information.


Default Extraction Methods
--------------------------

Babel comes with a few builtin extractors: ``python`` (which extracts
messages from Python source files), ``javascript``, and ``ignore`` (which
extracts nothing).

The ``python`` extractor is by default mapped to the glob pattern ``**.py``,
meaning it'll be applied to all files with the ``.py`` extension in any
directory. If you specify your own mapping configuration, this default mapping
is discarded, so you need to explicitly add it to your mapping (as shown in the
example above.)


.. _`referencing extraction methods`:

Referencing Extraction Methods
------------------------------

Generally, packages publish Babel extractors as Python entry points,
and so you can use a short name such as “genshi” to refer to them.

If the package implementing an extraction method has not been installed in a
way that has kept its entry point mapping intact, you need to map the short
names to fully qualified function names in an extract section in the mapping
configuration. For example:

.. code-block:: ini

    # Some custom extraction method

    [extractors]
    custom = mypackage.module:extract_custom

    [custom: **.ctm]
    some_option = foo

Note that the builtin extraction methods ``python`` and ``ignore`` are always
available, and you should never need to explicitly define them in the
``[extractors]`` section.


--------------------------
Writing Extraction Methods
--------------------------

Adding new methods for extracting localizable methods is easy. First, you'll
need to implement a function that complies with the following interface:

.. code-block:: python

    def extract_xxx(fileobj, keywords, comment_tags, options):
        """Extract messages from XXX files.

        :param fileobj: the file-like object the messages should be extracted
                        from
        :param keywords: a list of keywords (i.e. function names) that should
                         be recognized as translation functions
        :param comment_tags: a list of translator tags to search for and
                             include in the results
        :param options: a dictionary of additional options (optional)
        :return: an iterator over ``(lineno, funcname, message, comments)``
                 tuples
        :rtype: ``iterator``
        """

.. note:: Any strings in the tuples produced by this function must be either
          ``unicode`` objects, or ``str`` objects using plain ASCII characters.
          That means that if sources contain strings using other encodings, it
          is the job of the extractor implementation to do the decoding to
          ``unicode`` objects.

Next, you should register that function as an `entry point`_.
If using ``setup.py``, add something like the following to your ``setup.py``
script:

.. code-block:: python

    def setup(...

        entry_points = """
        [babel.extractors]
        xxx = your.package:extract_xxx
        """,

If using a ``pyproject.toml`` file, add something like the following:

.. code-block:: toml

    [project.entry-points."babel.extractors"]
    xxx = "your.package:extract_xxx"

That is, add your extraction method to the entry point group
``babel.extractors``, where the name of the entry point is the name that people
will use to reference the extraction method, and the value being the module and
the name of the function (separated by a colon) implementing the actual
extraction.

.. note:: As shown in `Referencing Extraction Methods`_, declaring an entry
          point is not  strictly required, as users can still reference the
          extraction  function directly. But whenever possible, the entry point
          should be  declared to make configuration more convenient.

.. _`setuptools`: https://setuptools.pypa.io/en/latest/setuptools.html


-------------------
Translator Comments
-------------------

First of all what are comments tags. Comments tags are excerpts of text to
search for in comments, only comments, right before the python :mod:`gettext`
calls, as shown on the following example:

.. code-block:: python

    # NOTE: This is a comment about `Foo Bar`
    _('Foo Bar')

The comments tag for the above example would be ``NOTE:``, and the translator
comment for that tag would be ``This is a comment about `Foo Bar```.

The resulting output in the catalog template would be something like::

    #. This is a comment about `Foo Bar`
    #: main.py:2
    msgid "Foo Bar"
    msgstr ""

Now, you might ask, why would I need that?

Consider this simple case; you have a menu item called “manual”. You know what
it means, but when the translator sees this they will wonder did you mean:

1. a document or help manual, or
2. a manual process?

This is the simplest case where a translation comment such as
“The installation manual” helps to clarify the situation and makes a translator
more productive.

.. note:: Whether translator comments can be extracted depends on the extraction
          method in use. The Python extractor provided by Babel does implement
          this feature, but others may not.
