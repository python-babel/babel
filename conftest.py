from _pytest.doctest import DoctestModule
from py.path import local

collect_ignore = ['tests/messages/data', 'setup.py']
babel_path = local(__file__).dirpath().join('babel')


def pytest_collect_file(path, parent):
    if babel_path.common(path) == babel_path:
        if path.ext == ".py":
            return DoctestModule(path, parent)
