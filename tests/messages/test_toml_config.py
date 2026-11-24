from __future__ import annotations

import logging
import pathlib
from io import BytesIO

import pytest

from babel.messages import frontend

toml_test_cases_path = pathlib.Path(__file__).parent / "toml-test-cases"
assert toml_test_cases_path.is_dir(), "toml-test-cases directory not found"


def parse_toml(cfg: bytes | str):
    if isinstance(cfg, str):
        cfg = cfg.encode("utf-8")
    return frontend._parse_mappings_from_toml(BytesIO(cfg))


def test_toml_mapping_multiple_patterns():
    """
    Test that patterns may be specified as a list in TOML,
    and are expanded to multiple entries in the method map.
    """
    method_map, options_map = parse_toml("""
[[mappings]]
method = "python"
pattern = ["xyz/**.py", "foo/**.py"]
""")
    assert method_map == [
        ('xyz/**.py', 'python'),
        ('foo/**.py', 'python'),
    ]


@pytest.mark.parametrize(
    ("keywords_val", "expected"),
    [
        pytest.param('"foo bar quz"', {'bar': None, 'foo': None, 'quz': None}, id='string'),
        pytest.param('["foo", "bar", "quz"]', {'bar': None, 'foo': None, 'quz': None}, id='list'),
        pytest.param('"foo:1,2 bar quz"', {'bar': None, 'foo': (1, 2), 'quz': None}, id='s-args'),
        pytest.param('["bar", "foo:1,2", "quz"]', {'bar': None, 'foo': (1, 2), 'quz': None}, id='l-args'),
        pytest.param('[]', None, id='empty'),
    ],
)
def test_toml_mapping_keywords_parsing(keywords_val, expected):
    method_map, options_map = parse_toml(f"""
[[mappings]]
method = "python"
pattern = ["**.py"]
keywords = {keywords_val}
""")
    assert options_map['**.py'].get('keywords') == expected


@pytest.mark.parametrize(
    ("add_comments_val", "expected"),
    [
        ('"SPECIAL SAUCE"', ['SPECIAL SAUCE']),  # TOML will allow this as a single string
        ('["SPECIAL", "SAUCE"]', ['SPECIAL', 'SAUCE']),
        ('[]', None),
    ],
)
def test_toml_mapping_add_comments_parsing(add_comments_val, expected):
    method_map, options_map = parse_toml(f"""
[[mappings]]
method = "python"
pattern = ["**.py"]
add_comments = {add_comments_val}
""")
    assert options_map['**.py'].get('add_comments') == expected


@pytest.mark.parametrize("test_case", tuple(toml_test_cases_path.glob("bad.*.toml")), ids=lambda p: p.name)
def test_bad_toml_test_case(test_case: pathlib.Path):
    """
    Test that bad TOML files raise a ValueError.
    """
    with pytest.raises(frontend.ConfigurationError):
        with test_case.open("rb") as f:
            frontend._parse_mappings_from_toml(
                f,
                filename=test_case.name,
                style="pyproject.toml" if "pyproject" in test_case.name else "standalone",
            )


@pytest.fixture
def in_tmp_path(tmp_path, monkeypatch) -> pathlib.Path:
    monkeypatch.delenv("BABEL_PYPROJECT_TOML", raising=False)
    monkeypatch.chdir(tmp_path)
    return tmp_path


def _parse_cli_config(command="extract"):
    cli = frontend.CommandLineInterface()
    cli.log = frontend.log
    cmdinst = cli.command_classes[command]()
    return cli._parse_config_from_pyproject_toml(cmdinst)


@pytest.mark.parametrize(
    ("path", "content", "expected"),
    [
        ("pyproject.toml", '[project]\nname = "test"\n', {}),
        ("pyproject.toml", '[tool.babel.compile_catalog]\ndomain = "test"\n', {}),
        ("pyproject.toml", '[tool.babel.extract_messages]\noutput_file = "x.pot"\n', {"output_file": "x.pot"}),
        ("pyproject.toml", '[tool.babel.extract_messages]\noutput-file = "x.pot"\n', {"output_file": "x.pot"}),
        ("../pyproject.toml", '[tool.babel.extract_messages]\noutput_file = "x.pot"\n', {}),  # no upward search
        (None, None, {}),  # no file
    ],
)
def test_cli_pyproject_toml_lookup(in_tmp_path, monkeypatch, path, content, expected):
    sub = in_tmp_path / "sub"
    sub.mkdir()
    monkeypatch.chdir(sub)
    if path:
        (sub / path).write_text(content)
    assert _parse_cli_config() == expected


@pytest.mark.parametrize(
    "content",
    [
        pytest.param(b"[tool.babel]\nx = [", id="malformed"),
        pytest.param(b'[tool.babel]\nx = "\xff"\n', id="non-utf8"),
        pytest.param(b'[tool]\nbabel = "x"\n', id="babel-not-a-table"),
        pytest.param(b'[tool.babel]\nextract_messages = "x"\n', id="command-not-a-table"),
    ],
)
def test_cli_ignores_bad_pyproject_toml_by_default(in_tmp_path, caplog, content):
    (in_tmp_path / "pyproject.toml").write_bytes(content)
    with caplog.at_level(logging.WARNING, logger="babel"):
        assert _parse_cli_config() == {}
    assert "Ignoring pyproject.toml configuration" in caplog.text


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("", {"output_file": "x.pot"}),
        ("skip", {}),
    ],
)
def test_cli_pyproject_toml_env_disable_or_default(in_tmp_path, monkeypatch, value, expected):
    (in_tmp_path / "pyproject.toml").write_text('[tool.babel.extract_messages]\noutput_file = "x.pot"\n')
    monkeypatch.setenv("BABEL_PYPROJECT_TOML", value)
    assert _parse_cli_config() == expected


@pytest.mark.parametrize(
    ("filename", "content", "match"),
    [
        ("pyproject.tml", None, "is not a file"),
        ("config.toml", "[tool.babel.extract_messages]\nx = [", "Error parsing TOML"),
    ],
)
def test_cli_pyproject_toml_env_errors_are_raised(in_tmp_path, monkeypatch, filename, content, match):
    (in_tmp_path / "pyproject.toml").write_text('[tool.babel.extract_messages]\noutput_file = "x.pot"\n')
    if content:
        (in_tmp_path / filename).write_text(content)
    monkeypatch.setenv("BABEL_PYPROJECT_TOML", str(in_tmp_path / filename))
    with pytest.raises(frontend.ConfigurationError, match=match):
        _parse_cli_config()


def test_cli_pyproject_toml_list_values_not_split(in_tmp_path):
    (in_tmp_path / "a b.py").touch()
    (in_tmp_path / "pyproject.toml").write_text(
        '[tool.babel.extract_messages]\n'
        'output_file = "x.pot"\n'
        'add_comments = ["NOTE TO TRANSLATORS:"]\n'
        'input_paths = ["a b.py"]\n',
    )
    cli = frontend.CommandLineInterface()
    cli.log = frontend.log
    cmdinst = cli._configure_command("extract", [])
    assert cmdinst.add_comments == ["NOTE TO TRANSLATORS:"]
    assert cmdinst.input_paths == ["a b.py"]
