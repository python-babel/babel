# gvar.py
import re
import locale
from babel.messages.catalog import VERSION

class gv:
    # Define the set of recognized flags for message formatting.
    RECOGNIZED_FLAGS = {
        'fuzzy', 'c-format', 'no-c-format', 'objc-format', 'no-objc-format',
        'java-format', 'no-java-format', 'no-java-printf-format', 'python-format', 'no-python-format',
        'no-python-brace-format', 'php-format', 'no-php-format', 'gcc-internal-format', 'no-gcc-internal-format',
        'qt-format', 'qt-plural-format', 'no-qt-format', 'boost-format', 'no-boost-format',
        'c++-format', 'no-c++-format', 'csharp-format', 'no-csharp-format', 'elisp-format',
        'no-elisp-format', 'gfc-internal-format', 'no-gfc-internal-format', 'javascript-format', 'no-javascript-format',
        'lua-format', 'no-lua-format', 'objc-format', 'no-objc-format', 'java-format',
        'perl-format', 'no-perl-format', 'perl-brace-format', 'no-perl-brace-format', 'ruby-format',
        'no-ruby-format', 'rust-format', 'no-rust-format', 'scheme-format', 'no-scheme-format',
        'sh-format', 'no-sh-format', 'smalltalk-format', 'no-smalltalk-format', 'tcl-format',
        'no-tcl-format', 'ycp-format', 'no-ycp-format', 'awk-format', 'no-awk-format',
        'lisp-format', 'no-lisp-format', 'librep-format', 'no-librep-format', 'object-pascal-format',
        'no-object-pascal-format', 'elisp-format', 'no-elisp-format', 'javascript-format', 'no-javascript-format',
        'lua-format', 'no-lua-format', 'gfc-internal-format', 'no-gfc-internal-format', 'smalltalk-format',
        'no-smalltalk-format', 'tcl-format', 'no-tcl-format', 'ycp-format', 'no-ycp-format',
        'awk-format', 'no-awk-format', 'lisp-format', 'no-lisp-format', 'smalltalk-format',
        'no-smalltalk-format', 'kde-format', 'no-kde-format', 'qt-format', 'no-qt-format'
    }

    # Parser configuration and state variables.
    BLOCKS = None  # Pre-split list of blocks from the PO file.
    IS_DEBUG = False  # Debug flag.
    IS_HOOK_EXEPT = True  # Hook exception flag.
    IS_MULTI_PROCESSING = False  # Flag to enable multiprocessing.
    LOGGER = None  # Global logger instance.
    CATALOG = None  # Babel Catalog instance.
    BATCH_DIVISION_REDUCTION = 3  # Reduction factor for batch size.
    IS_ABORT_ON_INVALID = True  # Flag to abort on invalid entries.
    all_messages = []  # List to store all parsed messages.
    all_errors = []  # List to store errors encountered during parsing.
    ABORT_EVENT = None  # Global event to signal an abort in multiprocessing.

    # Variables used for catalog header processing.
    IS_CATALOG_HEADER = False
    VALID_CATALOG_STRING_LIST = None

    # Additional error tracking.
    ERRORS = []
    IS_IGNORE_OBSOLETE = True

    # -------------------------------------------------------------------------
    # Precompiled regex patterns and constants for message fields
    # -------------------------------------------------------------------------
    escapped_new_line_pattern = re.compile(r'\\([\\trn"])')
    COMMENT_PATTERN = re.compile(r'^#(?:[ :,\.\~\|]*?.*)?$')
    MSGSTR_PLURAL_PATTERN = re.compile(r'msgstr\[(\d+)\]\s+"(.*)"')

    LEN_MSGCTXT = len("msgctxt")
    LEN_MSGID = len("msgid")
    LEN_MSGID_PLURAL = len("msgid_plural")
    LEN_MSGSTR = len("msgstr")

    # Global variables for catalog_parser
    DEFAULT_CAT_STRINGS = {
        'Project-Id-Version': 'Foobar 1.0',
        'Report-Msgid-Bugs-To': 'EMAIL@ADDRESS',
        'POT-Creation-Date': '1990-04-01 15:30+0000',
        'PO-Revision-Date': 'YEAR-MO-DA HO:MI+ZONE',
        'Last-Translator': 'FULL NAME <EMAIL@ADDRESS>',
        'Language-Team': 'LANGUAGE <LL@li.org>',
        'Language': 'en',
        'Plural-Forms': 'nplurals=1; plural=0;',
        'MIME-Version': '1.0',
        'Content-Type': 'text/plain; charset=utf-8',
        'Content-Transfer-Encoding': '8bit',
        'Generated-By': f'Babel {VERSION}\n',
        'X-Generator': 'Poedit 3.5\n',
    }
    DEFAULT_CAT_STRING_LIST = list(DEFAULT_CAT_STRINGS.keys())
    HEADER_SEPARATOR = ':'

    machine_language, machine_encoding = locale.getdefaultlocale()