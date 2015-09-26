import os
import sys
import array
import zipfile

PY2 = sys.version_info[0] == 2

_identity = lambda x: x


if not PY2:
    text_type = str
    string_types = (str,)
    integer_types = (int, )
    unichr = chr

    text_to_native = lambda s, enc: s

    iterkeys = lambda d: iter(d.keys())
    itervalues = lambda d: iter(d.values())
    iteritems = lambda d: iter(d.items())

    from io import StringIO, BytesIO
    import pickle

    izip = zip
    imap = map
    range_type = range

    cmp = lambda a, b: (a > b) - (a < b)

    array_tobytes = array.array.tobytes

else:
    text_type = unicode
    string_types = (str, unicode)
    integer_types = (int, long)

    text_to_native = lambda s, enc: s.encode(enc)
    unichr = unichr

    iterkeys = lambda d: d.iterkeys()
    itervalues = lambda d: d.itervalues()
    iteritems = lambda d: d.iteritems()

    from cStringIO import StringIO as BytesIO
    from StringIO import StringIO
    import cPickle as pickle

    from itertools import izip, imap
    range_type = xrange

    cmp = cmp

    array_tobytes = array.array.tostring


number_types = integer_types + (float,)


def _zip_split(path):
    for ext in ('zip', 'whl'):
        if '.' + ext + os.sep in path:
            return ext
    return None


def extract_nested_zipfile(path, parent_zip=None):
    """Returns a ZipFile specified by path, even if the path contains
    intermediary ZipFiles.  For example, /root/gparent.zip/parent.zip/child.zip
    will return a ZipFile that represents child.zip
    """

    def extract_inner_zipfile(parent_zip, child_zip_path):
        """Returns a ZipFile specified by child_zip_path that exists inside
        parent_zip.
        """
        memory_zip = StringIO()
        memory_zip.write(parent_zip.open(child_zip_path).read())
        return zipfile.ZipFile(memory_zip)

    split = _zip_split(path)
    if split:
        (parent_zip_path, child_zip_path) = os.path.relpath(path).split(
            split + os.sep, 1)
        parent_zip_path += split

        if not parent_zip:
            # This is the top-level, so read from disk
            parent_zip = zipfile.ZipFile(parent_zip_path)
        else:
            # We're already in a zip, so pull it out and recurse
            parent_zip = extract_inner_zipfile(parent_zip, parent_zip_path)

        return extract_nested_zipfile(child_zip_path, parent_zip)
    else:
        if parent_zip:
            return extract_inner_zipfile(parent_zip, path)
        else:
            # If there is no nesting, it's easy!
            return zipfile.ZipFile(path)


def zipopen(path, mode):
    """Open a file inside a zip file"""
    split = _zip_split(path)

    if split:
        zip_path, file_path = os.path.relpath(path).rsplit(split + os.sep, 1)
        zip_path += split

        z = extract_nested_zipfile(zip_path)
        return BytesIO(z.read(file_path))
    else:
        return open(path, mode)


def zipexists(path):
    """Check if a file exists inside a zip file."""
    split = _zip_split(path)

    if split:
        zip_path, file_path = os.path.relpath(path).rsplit(split + os.sep, 1)
        zip_path += split
        z = extract_nested_zipfile(zip_path)
        return file_path in z.namelist()
    else:
        return os.path.exists(path)

