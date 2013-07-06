collect_ignore = ['tests/messages/data']

def pytest_configure(config):
    import sys
    if sys.version_info[0] < 3:
        config.option.doctestmodules = True
