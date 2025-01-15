import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from tests.messages.consts import data_dir

Distribution = pytest.importorskip("setuptools").Distribution


@pytest.mark.parametrize("kwarg,expected", [
    ("LW_", ("LW_",)),
    ("LW_ QQ Q", ("LW_", "QQ", "Q")),
    ("yiy         aia", ("yiy", "aia")),
])
def test_extract_distutils_keyword_arg_388(kwarg, expected):
    from babel.messages import frontend, setuptools_frontend

    # This is a regression test for https://github.com/python-babel/babel/issues/388

    # Note that distutils-based commands only support a single repetition of the same argument;
    # hence `--keyword ignored` will actually never end up in the output.

    cmdline = (
        f"extract_messages --no-default-keywords --keyword ignored --keyword '{kwarg}' "
        "--input-dirs . --output-file django233.pot --add-comments Bar,Foo"
    )
    d = Distribution(attrs={
        "cmdclass": setuptools_frontend.COMMANDS,
        "script_args": shlex.split(cmdline),
    })
    d.parse_command_line()
    assert len(d.commands) == 1
    cmdinst = d.get_command_obj(d.commands[0])
    cmdinst.ensure_finalized()
    assert isinstance(cmdinst, frontend.ExtractMessages)
    assert isinstance(cmdinst, setuptools_frontend.extract_messages)
    assert set(cmdinst.keywords.keys()) == set(expected)

    # Test the comma-separated comment argument while we're at it:
    assert set(cmdinst.add_comments) == {"Bar", "Foo"}


def test_setuptools_commands(tmp_path, monkeypatch):
    """
    Smoke-tests all of the setuptools versions of the commands in turn.

    Their full functionality is tested better in `test_frontend.py`.
    """
    # Copy the test project to a temporary directory and work there
    dest = tmp_path / "dest"
    shutil.copytree(data_dir, dest)
    monkeypatch.chdir(dest)

    # When in Tox, we need to hack things a bit so as not to have the
    # sub-interpreter `sys.executable` use the tox virtualenv's Babel
    # installation, so the locale data is where we expect it to be.
    if "BABEL_TOX_INI_DIR" in os.environ:
        monkeypatch.setenv("PYTHONPATH", os.environ["BABEL_TOX_INI_DIR"])

    # Initialize an empty catalog
    subprocess.check_call([
        sys.executable,
        "setup.py",
        "init_catalog",
        "-i", os.devnull,
        "-l", "fi",
        "-d", "inited",
    ])
    po_file = Path("inited/fi/LC_MESSAGES/messages.po")
    orig_po_data = po_file.read_text()
    subprocess.check_call([
        sys.executable,
        "setup.py",
        "extract_messages",
        "-o", "extracted.pot",
    ])
    pot_file = Path("extracted.pot")
    pot_data = pot_file.read_text()
    assert "FooBar, TM" in pot_data  # should be read from setup.cfg
    assert "bugs.address@email.tld" in pot_data  # should be read from setup.cfg
    subprocess.check_call([
        sys.executable,
        "setup.py",
        "update_catalog",
        "-i", "extracted.pot",
        "-d", "inited",
    ])
    new_po_data = po_file.read_text()
    assert new_po_data != orig_po_data  # check we updated the file
    subprocess.check_call([
        sys.executable,
        "setup.py",
        "compile_catalog",
        "-d", "inited",
    ])
    assert po_file.with_suffix(".mo").exists()
