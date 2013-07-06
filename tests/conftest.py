import os
import pytest


@pytest.fixture
def os_environ(monkeypatch):
    mock_environ = dict(os.environ)
    monkeypatch.setattr(os, 'environ', mock_environ)
    return mock_environ
