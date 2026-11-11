from xml.etree import ElementTree

import pytest

from scripts import import_cldr


def supplemental_data(groups):
    return ElementTree.fromstring(
        f'<supplementalData><territoryContainment>{groups}'
        '</territoryContainment></supplementalData>',
    )


@pytest.mark.parametrize('reverse', [False, True])
def test_primary_territory_containment_ignores_auxiliary_records(reverse):
    groups = [
        '<group type="001" contains="019 150"/>',
        '<group type="001" contains="EU" status="grouping"/>',
        '<group type="001" contains="QU" status="deprecated"/>',
        '<group type="019" contains="005"/>',
        '<group type="019" contains="419" status="grouping"/>',
        '<group type="005" contains="AR BR" grouping="false"/>',
        '<group type="150" contains="155"/>',
        '<group type="155" contains="DE FR"/>',
        '<group type="155" contains="DD FX" status="deprecated"/>',
        '<group type="EU" contains="DE FR" grouping="true"/>',
        '<group type="419" contains="005" grouping="true"/>',
    ]
    if reverse:
        groups.reverse()
    children, parents = import_cldr.parse_territory_containment(
        supplemental_data(''.join(groups)),
    )
    assert children == {
        '001': ('019', '150'),
        '019': ('005',),
        '005': ('AR', 'BR'),
        '150': ('155',),
        '155': ('DE', 'FR'),
    }
    assert parents == {
        '019': '001', '150': '001', '005': '019', '155': '150',
        'AR': '005', 'BR': '005', 'DE': '155', 'FR': '155',
    }


def test_empty_territory_containment():
    assert import_cldr.parse_territory_containment(supplemental_data('')) == ({}, {})


@pytest.mark.parametrize('reverse', [False, True])
def test_territory_with_multiple_primary_parents_is_rejected(reverse):
    groups = ['<group type="005" contains="AR"/>', '<group type="019" contains="AR"/>']
    if reverse:
        groups.reverse()
    with pytest.raises(ValueError, match="Territory 'AR' has multiple primary parents"):
        import_cldr.parse_territory_containment(supplemental_data(''.join(groups)))


def test_duplicate_primary_group_is_rejected():
    groups = '<group type="001" contains="019"/><group type="001" contains="150"/>'
    with pytest.raises(ValueError, match="Duplicate primary territory group: '001'"):
        import_cldr.parse_territory_containment(supplemental_data(groups))


def test_world_cannot_have_a_parent():
    with pytest.raises(ValueError, match="world territory '001' cannot have a parent"):
        import_cldr.parse_territory_containment(
            supplemental_data('<group type="019" contains="001"/>'),
        )
