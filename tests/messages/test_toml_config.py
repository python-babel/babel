import pathlib
from io import BytesIO

import pytest

from babel.messages import frontend

toml_test_cases_path = pathlib.Path(__file__).parent / "toml-test-cases"
assert toml_test_cases_path.is_dir(), "toml-test-cases directory not found"


def test_toml_mapping_multiple_patterns():
    """
    Test that patterns may be specified as a list in TOML,
    and are expanded to multiple entries in the method map.
    """
    method_map, options_map = frontend._parse_mapping_toml(BytesIO(b"""
[[mappings]]
method = "python"
pattern = ["xyz/**.py", "foo/**.py"]
"""))
    assert len(method_map) == 2
    assert method_map[0] == ('xyz/**.py', 'python')
    assert method_map[1] == ('foo/**.py', 'python')


@pytest.mark.parametrize("test_case", toml_test_cases_path.glob("bad.*.toml"), ids=lambda p: p.name)
def test_bad_toml_test_case(test_case: pathlib.Path):
    """
    Test that bad TOML files raise a ValueError.
    """
    with pytest.raises(frontend.ConfigurationError):
        with test_case.open("rb") as f:
            frontend._parse_mapping_toml(
                f,
                filename=test_case.name,
                style="pyproject.toml" if "pyproject" in test_case.name else "standalone",
            )
