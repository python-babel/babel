import sys
from _pytest.doctest import DoctestModule
from py.path import local


PY2 = sys.version_info[0] < 3


collect_ignore = ['tests/messages/data']


def pytest_collect_file(path, parent):
    babel_path = local(__file__).dirpath().join('babel')
    config = parent.config
    if PY2:
        if babel_path.common(path) == babel_path:
            if path.ext == ".py":
                return DoctestModule(path, parent)
