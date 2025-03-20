"""
babel.messages.msg_parser
~~~~~~~~~~~~~~~~~~~~~~~~~~~
Parsing of gettext PO (Portable Object) files to produce Babel Message objects.
This module implements a finite state machine (FSM) to process PO file blocks line by line,
extracting and unescaping message fields and handling comments, context, and plural forms.
It also supports multiprocessing to parallelize the parsing process.

:copyright: (c) 2025 by the Babel Team.
:license: BSD, see LICENSE for more details.
"""

import sys
import re
import multiprocessing
import logging
import locale
from babel.messages import Message  # Babel’s Message class
from enum import IntFlag, auto
from babel.messages.gvar import gv  # Import the global variable class

# -------------------------------------------------------------------------
# Token Enumeration
# -------------------------------------------------------------------------
class Token(IntFlag):
    """
    Enumeration representing the various token types in a PO file.
    Tokens indicate message fields, comments, and special markers.
    """
    MSGCTXT = auto()
    MSGID = auto()
    MSGID_PLURAL = auto()
    MSGSTR = auto()
    MSGSTR_INDEX = auto()
    COMMENT_LOCATION = auto()
    COMMENT_FLAGS = auto()
    PREV_COMMENT = auto()
    COMMENT_AUTO_GEN = auto()
    # Any comment is a combination of the three comment types.
    COMMENT = COMMENT_LOCATION | COMMENT_FLAGS | COMMENT_AUTO_GEN | PREV_COMMENT
    CONTINUATION = auto()
    ERROR = auto()  # Token for grammar errors.
    # Tokens for obsolete messages.
    OBSOLETE_MSGID = auto()
    OBSOLETE_MSGSTR = auto()
    OBSOLETE_MSGCTXT = auto()
    OBSOLETE_MSGID_PLURAL = auto()
    OBSOLETE_MSGSTR_PLURAL = auto()

    @classmethod
    def get(cls, txt_line: str) -> "Token":
        """
        Determine the token type based on the given line.
        Optimized by checking the first character of the line.
        """
        if not txt_line:
            return cls.ERROR
        first = txt_line[0]
        if first == '#':
            if txt_line.startswith("#~"):
                # Process obsolete message tokens.
                stripped = txt_line[2:].lstrip()
                if stripped.startswith("msgctxt"):
                    return cls.OBSOLETE_MSGCTXT
                elif stripped.startswith("msgid_plural"):
                    return cls.OBSOLETE_MSGID_PLURAL
                elif stripped.startswith("msgstr_plural"):
                    return cls.OBSOLETE_MSGSTR_PLURAL
                elif stripped.startswith("msgid"):
                    return cls.OBSOLETE_MSGID
                elif stripped.startswith("msgstr["):
                    return cls.MSGSTR_INDEX
                elif stripped.startswith("msgstr"):
                    return cls.OBSOLETE_MSGSTR
                elif stripped and stripped[0] == '"':
                    return cls.CONTINUATION
                else:
                    return cls.ERROR
            else:
                return cls.COMMENT
        elif first == 'm':
            if txt_line.startswith("msgctxt"):
                return cls.MSGCTXT
            elif txt_line.startswith("msgid_plural"):
                return cls.MSGID_PLURAL
            elif txt_line.startswith("msgid"):
                return cls.MSGID
            elif txt_line.startswith("msgstr["):
                return cls.MSGSTR_INDEX
            elif txt_line.startswith("msgstr"):
                return cls.MSGSTR
        elif first == '"':
            return cls.CONTINUATION
        return cls.ERROR


# -------------------------------------------------------------------------
# State Enumeration
# -------------------------------------------------------------------------
class State(IntFlag):
    """
    Enumeration representing the parser state for processing PO file blocks.
    Each state corresponds to a particular message component being processed.
    """
    INITIAL = auto()
    HEADER = auto()
    MCTX = auto()
    MSGID = auto()
    MSGID_PLURAL = auto()
    MSGSTR = auto()
    MSGSTR_INDEX = auto()
    # States for obsolete messages.
    OBSOLETE_MSGID = auto()
    OBSOLETE_MSGSTR = auto()
    OBSOLETE_MSGCTXT = auto()
    OBSOLETE_MSGID_PLURAL = auto()
    OBSOLETE_MSGSTR_PLURAL = auto()

    @classmethod
    def get(cls, txt_line: str) -> "State":
        """
        Determine the initial parser state based on the beginning of a line.
        """
        if txt_line.startswith("msgctxt"):
            return cls.MCTX
        elif txt_line.startswith("msgid_plural"):
            return cls.MSGID_PLURAL
        elif txt_line.startswith("msgid"):
            return cls.MSGID
        elif txt_line.startswith("msgstr["):
            return cls.MSGSTR_INDEX
        elif txt_line.startswith("msgstr"):
            return cls.MSGSTR
        elif txt_line.startswith("#"):
            return cls.HEADER
        else:
            return cls.INITIAL


# -------------------------------------------------------------------------
# Global Parser Configuration Variables are now in gv.py
# -------------------------------------------------------------------------
# (All global variables are now accessed via gv.<varname>)
# Note: Precompiled regex patterns and prefix constants are now in gv.

# -------------------------------------------------------------------------
# Helper Functions
# -------------------------------------------------------------------------
def extract_quoted_value(txt_line: str, prefix_len: int) -> str:
    """
    Extract and unescape a quoted value from a line by removing the prefix and quotes.
    """
    value = txt_line[prefix_len:].strip()
    if value and value[0] == '"' and value[-1] == '"':
        return unescape(value[1:-1])
    return ''


def _replace_escapes(match):
    """
    Helper function to replace escape sequences with their actual characters.
    """
    m = match.group(1)
    return {'n': '\n', 't': '\t', 'r': '\r'}.get(m, m)


def setup_logger(name="POFileParser", level=None):
    """
    Set up the global LOGGER with the specified name and logging level.
    """
    if level is None:
        level = logging.DEBUG if gv.IS_DEBUG else logging.INFO
    gv.LOGGER = logging.getLogger(name)
    gv.LOGGER.setLevel(level)
    for handler in gv.LOGGER.handlers[:]:
        gv.LOGGER.removeHandler(handler)
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s [%(processName)s] %(levelname)s: %(message)s")
    handler.setFormatter(formatter)
    gv.LOGGER.addHandler(handler)

    if not gv.IS_DEBUG:
        gv.LOGGER.disabled = True
    return gv.LOGGER


def custom_excepthook(exc_type, exc_value, exc_traceback):
    """
    Custom exception hook to print errors.
    """
    print(f"Error: {exc_value}")


def DEBUG_LOG(msg):
    import inspect
    """
    Log a debug message if debugging is enabled.
    """
    if gv.IS_DEBUG:
        caller_frame = inspect.currentframe().f_back
        caller_name = caller_frame.f_code.co_name
        gv.LOGGER.debug(f'{caller_name}() {msg}')


def worker_init(abort_event):
    """
    Initializer function for worker processes in multiprocessing.
    """
    gv.ABORT_EVENT = abort_event
    setup_logger(name="POFileParser", level=logging.DEBUG)


def init_parser(blocks,
                catalog=None,
                is_debug=False,
                batch_size_division=2,
                is_multi_processing=True,
                is_hook_except=True,
                ignore_obsolete=True,
                abort_on_invalid=True):
    """
    Initialize the global parser configuration.
    """
    gv.BATCH_DIVISION_REDUCTION = batch_size_division
    gv.BLOCKS = blocks
    gv.IS_DEBUG = is_debug
    gv.IS_MULTI_PROCESSING = is_multi_processing
    gv.IS_HOOK_EXEPT = is_hook_except
    gv.CATALOG = catalog
    gv.IS_IGNORE_OBSOLETE = ignore_obsolete
    gv.IS_ABORT_ON_INVALID = abort_on_invalid
    gv.ERRORS = []
    setup_logger(level=logging.DEBUG if gv.IS_DEBUG else logging.INFO)

    if gv.IS_HOOK_EXEPT:
        sys.excepthook = custom_excepthook


def unescape(string: str) -> str:
    r"""
    Reverse escape the given string by replacing escape sequences with their actual characters.
    """
    if '\\' not in string:
        return string
    return gv.escapped_new_line_pattern.sub(_replace_escapes, string)


def parse_header_msgstr(header: str) -> dict:
    """
    Parse a header msgstr (multi-line) into a dictionary of key-value pairs.
    """
    result = {}
    for txt_line in header.split("\n"):
        txt_line = txt_line.strip()
        valid_line = txt_line and (":" in txt_line)
        if valid_line:
            key, value = txt_line.split(":", 1)
            result[key.strip()] = value.strip()
    return result


# -------------------------------------------------------------------------
# Comment Handlers
# -------------------------------------------------------------------------
def _handle_comment(txt_line: str, abs_lineno: int, msg: dict, dyn_state: dict) -> None:
    """
    Process a comment line and update the message dictionary accordingly.
    """
    if txt_line.startswith("#:"):
        _handle_locations(txt_line, abs_lineno, msg, dyn_state)
    elif txt_line.startswith("#,"):
        _handle_flags(txt_line, abs_lineno, msg, dyn_state)
    elif txt_line.startswith("#."):
        _handle_auto_comment(txt_line, abs_lineno, msg, dyn_state)
    elif txt_line.startswith("#|"):
        _handle_prev_field(txt_line, abs_lineno, msg, dyn_state)
    elif txt_line.startswith("#"):
        _handle_user_comment(txt_line, abs_lineno, msg, dyn_state)
    else:
        raise ValueError(f"Unrecognized comment format at line number {abs_lineno}: {txt_line!r}")


def _handle_locations(txt_line: str, abs_lineno: int, msg: dict, dyn_state: dict) -> None:
    """
    Handle location comments (starting with "#:") and update message locations.
    """
    DEBUG_LOG(f"ENTER at line number {abs_lineno}: {txt_line!r}")
    occ_line = txt_line[2:].strip()
    for token in occ_line.split():
        if ':' in token:
            parts = token.rsplit(":", 1)
            try:
                lineno_val = int(parts[1])
            except ValueError:
                lineno_val = None
            msg['locations'].append((parts[0], lineno_val))
        else:
            msg['locations'].append((token, None))
    DEBUG_LOG(f"EXIT at line number {abs_lineno} with locations = {msg['locations']}")


def _handle_flags(txt_line: str, abs_lineno: int, msg: dict, dyn_state: dict) -> None:
    """
    Process flag comments (starting with "#,") and validate them against recognized flags.
    """
    DEBUG_LOG(f"ENTER at line number {abs_lineno}: {txt_line!r}")
    flags = [f.strip() for f in txt_line[2:].strip().split(",") if f.strip()]
    # Uncomment the following lines to enforce recognized flags:
    # for flag in flags:
    #     if flag not in RECOGNIZED_FLAGS:
    #         raise ValueError(f"Unrecognized flag {flag!r} at line number {abs_lineno}")
    msg['flags'].extend(flags)
    DEBUG_LOG(f"EXIT at line number {abs_lineno} with flags = {msg['flags']}")


def _handle_auto_comment(txt_line: str, abs_lineno: int, msg: dict, dyn_state: dict) -> None:
    """
    Handle automatic comments (starting with "#.") and update the message.
    """
    DEBUG_LOG(f"ENTER at line number {abs_lineno}: {txt_line!r}")
    comment_text = txt_line[2:].strip()
    msg['auto_comments'].append(comment_text)
    DEBUG_LOG(f"EXIT at line number {abs_lineno} with auto_comments = {msg['auto_comments']}")


def _handle_prev_field(txt_line: str, abs_lineno: int, msg: dict, dyn_state: dict) -> None:
    """
    Handle previous-field lines (starting with "#|") for all fields.
    """
    DEBUG_LOG(f"ENTER previous field at line number {abs_lineno}: {txt_line!r}")
    prev_text = txt_line[2:].strip()
    for marker in ("msgid_plural", "msgstr_plural", "msgctxt", "msgid", "msgstr"):
        if prev_text.startswith(marker):
            msg.setdefault('previous_id', []).append((marker, prev_text[len(marker):].strip()))
            DEBUG_LOG(f"EXIT previous field at line number {abs_lineno} with previous_id = {msg.get('previous_id')}")
            return
    msg.setdefault('previous_id', []).append(("unknown", prev_text))
    DEBUG_LOG(f"EXIT previous field at line number {abs_lineno} with previous_id = {msg.get('previous_id')}")


def _handle_user_comment(txt_line: str, abs_lineno: int, msg: dict, dyn_state: dict) -> None:
    """
    Handle user comments (starting with "#") and update the message.
    """
    DEBUG_LOG(f"ENTER at line number {abs_lineno}: {txt_line!r}")
    comment_text = txt_line[1:].strip()
    msg['user_comments'].append(comment_text)
    DEBUG_LOG(f"EXIT at line number {abs_lineno} with user_comments = {msg['user_comments']}")


# -------------------------------------------------------------------------
# Field Handlers for Normal Messages
# -------------------------------------------------------------------------
def _handle_msgctxt(txt_line: str, abs_lineno: int, msg: dict, dyn_state: dict) -> None:
    """
    Handle the msgctxt field in a message block.
    """
    DEBUG_LOG(f"ENTER at line number {abs_lineno}: {txt_line!r}")
    value = extract_quoted_value(txt_line, gv.LEN_MSGCTXT)
    msg['msgctxt'] = value
    dyn_state["current"] = State.MCTX
    DEBUG_LOG(f"EXIT at line number {abs_lineno} with msg['msgctxt'] = {value}")


def _handle_msgid(txt_line: str, abs_lineno: int, msg: dict, dyn_state: dict) -> None:
    """
    Handle the msgid field in a message block.
    """
    DEBUG_LOG(f"_handle_msgid: ENTER at line number {abs_lineno}: {txt_line!r}")
    if msg['msgid'] is None:
        msg['lineno'] = abs_lineno
    value = extract_quoted_value(txt_line, gv.LEN_MSGID)
    msg['msgid'] = value
    dyn_state["current"] = State.MSGID
    DEBUG_LOG(f"EXIT at line number {abs_lineno} with msg['msgid'] = {value}")


def _handle_msgid_plural(txt_line: str, abs_lineno: int, msg: dict, dyn_state: dict) -> None:
    """
    Handle the msgid_plural field in a message block.
    """
    DEBUG_LOG(f"ENTER at line number {abs_lineno}: {txt_line!r}")
    value = extract_quoted_value(txt_line, gv.LEN_MSGID_PLURAL)
    msg['msgid_plural'] = value
    dyn_state["current"] = State.MSGID_PLURAL
    DEBUG_LOG(f"EXIT at line number {abs_lineno} with msg['msgid_plural'] = {value}")


def _handle_msgstr(txt_line: str, abs_lineno: int, msg: dict, dyn_state: dict) -> None:
    """
    Handle the msgstr field in a message block.
    """
    DEBUG_LOG(f"ENTER at line number {abs_lineno}: {txt_line!r}")
    value = extract_quoted_value(txt_line, gv.LEN_MSGSTR)
    msg['msgstr'] = value
    dyn_state["current"] = State.MSGSTR
    DEBUG_LOG(f"EXIT at line number {abs_lineno} with msg['msgstr'] = {value}")


def _handle_msgstr_plural(txt_line: str, abs_lineno: int, msg: dict, dyn_state: dict) -> None:
    """
    Handle plural msgstr fields in a message block.
    """
    DEBUG_LOG(f"ENTER at line number {abs_lineno}: {txt_line!r}")
    m = gv.MSGSTR_PLURAL_PATTERN.match(txt_line)
    if m:
        index = int(m.group(1))
        value = unescape(m.group(2))
        msg.setdefault('msgstr_plural', {})[index] = value
        dyn_state["current"] = State.MSGSTR_INDEX
        dyn_state["plural_index"] = index
        DEBUG_LOG(f"EXIT at line number {abs_lineno} with msg['msgstr_plural'][{index}] = {value}")
    else:
        DEBUG_LOG(f"EXIT at line number {abs_lineno} with no match")


# -------------------------------------------------------------------------
# Handlers for Obsolete Messages
# -------------------------------------------------------------------------
def _handle_obsolete_msgid(txt_line: str, abs_lineno: int, msg: dict, dyn_state: dict) -> None:
    """
    Handle an obsolete msgid field.
    """
    DEBUG_LOG(f"ENTER at line number {abs_lineno}: {txt_line!r}")
    stripped = txt_line[2:].lstrip()
    if msg.get('msgid') is None:
        msg['lineno'] = abs_lineno
    value = extract_quoted_value(stripped, gv.LEN_MSGID)
    msg['msgid'] = value
    msg["obsolete"] = True
    dyn_state["current"] = State.OBSOLETE_MSGID
    DEBUG_LOG(f"EXIT at line number {abs_lineno} with msg['msgid'] = {value}")


def _handle_obsolete_msgstr(txt_line: str, abs_lineno: int, msg: dict, dyn_state: dict) -> None:
    """
    Handle an obsolete msgstr field.
    """
    DEBUG_LOG(f"_handle_obsolete_msgstr: ENTER at line number {abs_lineno}: {txt_line!r}")
    stripped = txt_line[2:].lstrip()
    value = extract_quoted_value(stripped, gv.LEN_MSGSTR)
    msg['msgstr'] = value
    msg["obsolete"] = True
    dyn_state["current"] = State.OBSOLETE_MSGSTR
    DEBUG_LOG(f"EXIT at line number {abs_lineno} with msg['msgstr'] = {value}")


def _handle_obsolete_msgctxt(txt_line: str, abs_lineno: int, msg: dict, dyn_state: dict) -> None:
    """
    Handle an obsolete msgctxt field.
    """
    DEBUG_LOG(f"ENTER at line number {abs_lineno}: {txt_line!r}")
    stripped = txt_line[2:].lstrip()  # remove "#~"
    value = extract_quoted_value(stripped, gv.LEN_MSGCTXT)
    msg['msgctxt'] = value
    msg["obsolete"] = True
    dyn_state["current"] = State.OBSOLETE_MSGCTXT
    DEBUG_LOG(f"EXIT at line number {abs_lineno} with msg['msgctxt'] = {value}")


def _handle_obsolete_msgid_plural(txt_line: str, abs_lineno: int, msg: dict, dyn_state: dict) -> None:
    """
    Handle an obsolete msgid_plural field.
    """
    DEBUG_LOG(f"ENTER at line number {abs_lineno}: {txt_line!r}")
    stripped = txt_line[2:].lstrip()  # remove "#~"
    value = extract_quoted_value(stripped, gv.LEN_MSGID_PLURAL)
    msg['msgid_plural'] = value
    msg["obsolete"] = True
    dyn_state["current"] = State.OBSOLETE_MSGID_PLURAL
    DEBUG_LOG(f"EXIT at line number {abs_lineno} with msg['msgid_plural'] = {value}")


def _handle_obsolete_msgstr_plural(txt_line: str, abs_lineno: int, msg: dict, dyn_state: dict) -> None:
    """
    Handle an obsolete msgstr_plural field.
    """
    DEBUG_LOG(f"ENTER at line number {abs_lineno}: {txt_line!r}")
    stripped = txt_line[2:].lstrip()  # remove "#~"
    obs_plural_pattern = re.compile(r'msgstr_plural\[(\d+)\]\s+"(.*)"')
    m = obs_plural_pattern.match(stripped)
    if m:
        index = int(m.group(1))
        value = unescape(m.group(2))
        msg.setdefault('msgstr_plural', {})[index] = value
        msg["obsolete"] = True
        dyn_state["current"] = State.OBSOLETE_MSGSTR_PLURAL
        dyn_state["plural_index"] = index
        DEBUG_LOG(f"EXIT at line number {abs_lineno} with msg['msgstr_plural'][{index}] = {value}")
    else:
        DEBUG_LOG(f"EXIT at line number {abs_lineno} with no match for OBSOLETE_MSGSTR_PLURAL")


# -------------------------------------------------------------------------
# Continuation Handler (supports obsolete states)
# -------------------------------------------------------------------------
def _handle_continuation(txt_line: str, absolute_line: int, msg: dict, dyn_state: dict) -> None:
    """
    Handle a line continuation for multi-line message fields.
    """
    current_state = dyn_state.get("current")
    allowed_states = {State.MCTX, State.MSGID, State.MSGID_PLURAL, State.MSGSTR, State.MSGSTR_INDEX,
                      State.OBSOLETE_MSGID, State.OBSOLETE_MSGSTR,
                      State.OBSOLETE_MSGCTXT, State.OBSOLETE_MSGID_PLURAL, State.OBSOLETE_MSGSTR_PLURAL}
    if current_state not in allowed_states:
        raise ValueError(f"Line continuation at line number {absolute_line} not allowed in state {current_state.name}")

    is_obsolete = current_state.name.startswith('OBSOLETE')
    if is_obsolete:
        txt_line = txt_line[2:].strip()
    if not (txt_line.startswith('"') and txt_line.endswith('"')):
        raise ValueError(
            f"Invalid continuation line for state {current_state.name} at line number {absolute_line}: {txt_line!r}. Missing quotes.")
    value = unescape(txt_line[1:-1])
    if current_state == State.MCTX:
        msg['msgctxt'] = (msg.get('msgctxt') or "") + value
    elif current_state in {State.MSGID, State.OBSOLETE_MSGID}:
        msg['msgid'] = (msg.get('msgid') or "") + value
    elif current_state == State.MSGID_PLURAL:
        msg['msgid_plural'] = (msg.get('msgid_plural') or "") + value
    elif current_state in {State.MSGSTR, State.OBSOLETE_MSGSTR}:
        if gv.IS_CATALOG_HEADER:
            is_valid = (gv.HEADER_SEPARATOR in value)
            if is_valid:
                front_part = value.split(gv.HEADER_SEPARATOR)[0]
                is_valid = front_part in gv.VALID_CATALOG_STRING_LIST
                if not is_valid:
                    raise ValueError(
                        f"Processing Catalog Header, {value!r} is not a valid header prefix, in state {current_state.name} at line number {absolute_line}")
            else:
                raise ValueError(f"Processing Catalog Header, missing {gv.HEADER_SEPARATOR!r} in text line {value!r}, at state {current_state.name} at line number {absolute_line}")
        msg['msgstr'] = (msg.get('msgstr') or "") + value
    elif current_state == State.MSGSTR_INDEX:
        plural_index = dyn_state.get("plural_index")
        if plural_index is not None:
            if plural_index in msg.get('msgstr_plural', {}):
                msg['msgstr_plural'][plural_index] += value
            else:
                msg.setdefault('msgstr_plural', {})[plural_index] = value
        else:
            raise ValueError(f"Missing plural index in state {current_state.name} at line number {absolute_line}")
    elif current_state in {State.OBSOLETE_MSGCTXT}:
        msg['msgctxt'] = (msg.get('msgctxt') or "") + value
    elif current_state in {State.OBSOLETE_MSGID_PLURAL}:
        msg['msgid_plural'] = (msg.get('msgid_plural') or "") + value
    elif current_state in {State.OBSOLETE_MSGSTR_PLURAL}:
        plural_index = dyn_state.get("plural_index")
        if plural_index is not None:
            if plural_index in msg.get('msgstr_plural', {}):
                msg['msgstr_plural'][plural_index] += value
            else:
                msg.setdefault('msgstr_plural', {})[plural_index] = value
        else:
            raise ValueError(f"Missing plural index in state {current_state.name} at line number {absolute_line}")
    DEBUG_LOG(f"EXIT at line number {absolute_line} with added value = {value!r}")


# -------------------------------------------------------------------------
# Nested Transition Table Using Enums
# -------------------------------------------------------------------------
NESTED_TRANSITION_TABLE = {
    State.INITIAL: {
        Token.MSGCTXT: (_handle_msgctxt, State.MCTX),
        Token.MSGID: (_handle_msgid, State.MSGID),
        Token.OBSOLETE_MSGID: (_handle_obsolete_msgid, State.OBSOLETE_MSGID),
        Token.OBSOLETE_MSGCTXT: (_handle_obsolete_msgctxt, State.OBSOLETE_MSGCTXT),
        Token.OBSOLETE_MSGID_PLURAL: (_handle_obsolete_msgid_plural, State.OBSOLETE_MSGID_PLURAL),
        Token.OBSOLETE_MSGSTR_PLURAL: (_handle_obsolete_msgstr_plural, State.OBSOLETE_MSGSTR_PLURAL),
    },
    State.MCTX: {
        Token.MSGID: (_handle_msgid, State.MSGID),
    },
    State.MSGID: {
        Token.CONTINUATION: (_handle_continuation, State.MSGID),
        Token.MSGID_PLURAL: (_handle_msgid_plural, State.MSGID_PLURAL),
        Token.MSGSTR: (_handle_msgstr, State.MSGSTR),
        Token.MSGSTR_INDEX: (_handle_msgstr_plural, State.MSGSTR_INDEX),
    },
    State.MSGID_PLURAL: {
        Token.CONTINUATION: (_handle_continuation, State.MSGID_PLURAL),
        Token.MSGSTR_INDEX: (_handle_msgstr_plural, State.MSGSTR_INDEX),
    },
    State.MSGSTR: {
        Token.CONTINUATION: (_handle_continuation, State.MSGSTR),
    },
    State.MSGSTR_INDEX: {
        Token.CONTINUATION: (_handle_continuation, State.MSGSTR_INDEX),
        Token.MSGSTR_INDEX: (_handle_msgstr_plural, State.MSGSTR_INDEX),
    },
    State.OBSOLETE_MSGID: {
        Token.CONTINUATION: (_handle_continuation, State.OBSOLETE_MSGID),
        Token.OBSOLETE_MSGSTR: (_handle_obsolete_msgstr, State.OBSOLETE_MSGSTR),
    },
    State.OBSOLETE_MSGSTR: {
        Token.CONTINUATION: (_handle_continuation, State.OBSOLETE_MSGSTR),
    },
    State.OBSOLETE_MSGCTXT: {
        Token.CONTINUATION: (_handle_continuation, State.OBSOLETE_MSGCTXT),
    },
    State.OBSOLETE_MSGID_PLURAL: {
        Token.CONTINUATION: (_handle_continuation, State.OBSOLETE_MSGID_PLURAL),
        Token.OBSOLETE_MSGSTR: (_handle_obsolete_msgstr, State.OBSOLETE_MSGSTR),
    },
    State.OBSOLETE_MSGSTR_PLURAL: {
        Token.CONTINUATION: (_handle_continuation, State.OBSOLETE_MSGSTR_PLURAL),
    },
}


def printErrors():
    """
    Print any errors encountered during parsing.
    """
    if gv.all_errors:
        print("Errors encountered:", file=sys.stderr)
        for err in gv.all_errors:
            print(err, file=sys.stderr)


msg_valid_state = { State.MSGID,
                         State.MSGSTR,
                         State.OBSOLETE_MSGSTR,
                         State.OBSOLETE_MSGID,
                         State.OBSOLETE_MSGCTXT,
                         State.OBSOLETE_MSGID_PLURAL,
                         State.OBSOLETE_MSGSTR_PLURAL}
header_valid_state = {State.MSGID, State.MSGSTR}

# -------------------------------------------------------------------------
# State Machine for Processing a Block (Line-by-Line)
# -------------------------------------------------------------------------
def process_block(block: str, base_line: int,
                  is_catalog_header=False,
                  valid_catalog_header_list=None,
                  valid_catalog_string_list=None,
                  header_separator=None) -> Message:
    """
    Process a single block (entry) using a finite state machine (FSM).
    """
    if gv.IS_MULTI_PROCESSING and gv.ABORT_EVENT and gv.ABORT_EVENT.is_set():
        return None  # Skip processing if abort event is set

    gv.IS_CATALOG_HEADER = is_catalog_header
    gv.VALID_CATALOG_STRING_LIST = valid_catalog_string_list
    gv.HEADER_SEPARATOR = header_separator

    cur_state = State.INITIAL
    msg = {
        'msgctxt': None,
        'msgid': None,
        'msgid_plural': None,
        'msgstr': '',
        'msgstr_plural': {},
        'locations': [],
        'flags': [],
        'auto_comments': [],
        'user_comments': [],
        'previous_id': [],
        'lineno': None,
        'obsolete': False,
    }
    dyn_state = {"current": None, "plural_index": None}
    lines = block.splitlines()
    nt_table = NESTED_TRANSITION_TABLE  # Local alias for faster lookup.

    err_line = 0
    err_line_txt = None
    err_token = Token.ERROR
    for i, txt_line in enumerate(lines):
        abs_lineno = base_line + i
        s = txt_line.strip()
        if not s:
            raise ValueError(f"Unexpected empty line at line number: {abs_lineno}: {txt_line!r}")
        err_line = abs_lineno
        err_line_txt = txt_line
        token = Token.get(s)
        err_token = token
        if token == Token.ERROR:
            raise ValueError(f"File structure error at line number {err_line}: {err_line_txt!r}")
        if token == Token.COMMENT:
            _handle_comment(s, abs_lineno, msg, dyn_state)
            continue
        sub_table = nt_table.get(cur_state)
        if sub_table is None or token not in sub_table:
            raise ValueError(f"Unexpected token {token.name} at line number {err_line} in state {err_token.name}: {err_line_txt!r}")
        handler, new_state = sub_table[token]
        handler(s, abs_lineno, msg, dyn_state)
        cur_state = new_state


    # --- NEW CHECK FOR ABRUPT BLOCK ENDING ---
    expected_final_states = msg_valid_state if not gv.IS_CATALOG_HEADER else header_valid_state
    if cur_state not in expected_final_states:
        if msg['msgid'] is not None and cur_state in {State.MSGID, State.MSGID_PLURAL}:
            raise ValueError(f"Abrupt ending of block at line number {err_line}: MSGID exists but no MSGSTR was found. Last text line: {err_line_txt!r}")
        report_expecting_set = [s.name for s in expected_final_states]
        is_multiple = len(report_expecting_set) > 1
        state_multiple_stmt = "one of these states" if is_multiple else "this state"
        raise ValueError(f"Incomplete entry at line number {err_line}, ended in state {err_token.name}, {err_line_txt!r},\n"
                         f"expecting in {state_multiple_stmt} {report_expecting_set}")
    # --- END NEW CHECK ---

    try:
        if msg.get('msgid_plural'):
            expected_n = gv.CATALOG.num_plurals  # Get number of plurals from catalog header.
            plural_indexes = sorted(msg['msgstr_plural'].keys())
            if plural_indexes != list(range(expected_n)):
                raise ValueError(
                    f"Invalid plural indexes at line number {msg['lineno']}: expected {list(range(expected_n))}, got {plural_indexes} for {msg['msgstr_plural']}")
            translations = tuple(msg['msgstr_plural'][i] for i in sorted(msg['msgstr_plural']))
            mesg = Message(
                [msg['msgid'], msg['msgid_plural']],
                string=translations,
                locations=msg['locations'],
                flags=msg['flags'],
                auto_comments=msg['auto_comments'],
                user_comments=msg['user_comments'],
                previous_id=msg['previous_id'],
                lineno=msg['lineno'],
                context=msg['msgctxt']
            )
        else:
            mesg = Message(
                msg['msgid'],
                string=msg['msgstr'],
                locations=msg['locations'],
                flags=set(msg['flags']),
                auto_comments=msg['auto_comments'],
                user_comments=msg['user_comments'],
                previous_id=msg['previous_id'],
                lineno=msg['lineno'],
                context=msg['msgctxt']
            )
        if msg.get("obsolete"):
            mesg.obsolete = True
        return mesg
    except Exception as e:
        if gv.IS_ABORT_ON_INVALID:
            gv.ABORT_EVENT.set()  # Signal other processes to stop.
            raise e
        else:
            gv.all_errors.append(e)
            return None


# -------------------------------------------------------------------------
# Multiprocessing Helper and Main Parse Function
# -------------------------------------------------------------------------
def process_batch(batch, process_block_func, is_debug) -> list:
    """
    Process a batch of blocks and return a list of parsed Message instances.
    """
    gv.IS_DEBUG = is_debug
    results = [process_block_func(block, start_line) for start_line, block in batch]
    if gv.IS_DEBUG:
        for handler in gv.LOGGER.handlers:
            handler.flush()
    return results


def process_batch_wrapper(batch):
    """
    Wrapper function for processing a batch of blocks.
    """
    return process_batch(batch, process_block, gv.IS_DEBUG)


def split_into_batches(lst, num_batches):
    """
    Split the list 'lst' into 'num_batches' contiguous batches.
    """
    n = len(lst)
    batch_size = n // num_batches
    remainder = n % num_batches
    batches = []
    start = 0
    for i in range(num_batches):
        extra = 1 if i < remainder else 0
        end = start + batch_size + extra
        batches.append(lst[start:end])
        start = end
    return batches


def parse() -> tuple:
    """
    Parse the pre-split PO file blocks into Message instances and collect any errors.
    """
    blocks = gv.BLOCKS
    DEBUG_LOG(f"Total blocks found: {len(blocks)}")

    if gv.IS_MULTI_PROCESSING:
        gv.ABORT_EVENT = multiprocessing.Event()
        gv.ABORT_EVENT.clear()

        num_cores = multiprocessing.cpu_count()
        num_batches = max(1, num_cores - 2)
        num_batches = (num_batches // gv.BATCH_DIVISION_REDUCTION if num_batches >= 5 else num_batches)
        print(f"Using {num_batches} batch(es) (cpu_count: {num_cores})")
        batches = split_into_batches(blocks, num_batches)
        print(f'number of batches: {len(batches)}, batch_size: {len(batches[0])}')
        pool = multiprocessing.Pool(processes=num_batches,
                                    initializer=worker_init,
                                    initargs=(gv.ABORT_EVENT,))
        results = []
        try:
            results = pool.map(process_batch_wrapper, batches)
        except Exception as e:
            gv.ERRORS.append(e)
            if gv.IS_ABORT_ON_INVALID:
                gv.ABORT_EVENT.set()
                pool.terminate()
                pool.join()
                raise e
            else:
                gv.all_errors.append(e)

        pool.close()
        pool.join()
        for batch_results in results:
            gv.all_messages.extend(batch_results)
    else:
        gv.ABORT_EVENT = multiprocessing.Event()
        DEBUG_LOG("Processing blocks sequentially.")
        for start_line, block in blocks:
            try:
                gv.all_messages.append(process_block(block, start_line))
            except Exception as e:
                if gv.IS_ABORT_ON_INVALID:
                    raise e
                else:
                    gv.all_errors.append(e)
    gv.all_messages = [m for m in gv.all_messages if m is not None]
    gv.all_messages.sort(key=lambda m: m.lineno if m.lineno is not None else 0)
    return gv.all_messages, gv.all_errors
