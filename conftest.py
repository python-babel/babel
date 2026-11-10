import os
from pathlib import Path

import pytest
from _pytest.doctest import DoctestModule

collect_ignore = [
    'babel/messages/setuptools_frontend.py',
    'tests/messages/data',
]
babel_path = Path(__file__).parent / 'babel'


# Via the stdlib implementation of Path.is_relative_to in Python 3.9
def _is_relative(p1: Path, p2: Path) -> bool:
    try:
        p1.relative_to(p2)
        return True
    except ValueError:
        return False


def pytest_collect_file(file_path: Path, parent):
    if _is_relative(file_path, babel_path) and file_path.suffix == '.py':
        return DoctestModule.from_parent(parent, path=file_path)


@pytest.fixture(autouse=True)
def restore_environ():
    # Clean up after after tests that modify environment
    # variables (e.g. core.default_locale doctest)
    saved = os.environ.copy()
    yield
    os.environ.clear()
    os.environ.update(saved)
