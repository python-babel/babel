import datetime
import itertools
import random
from io import BytesIO

import pytest

from babel.messages.catalog import Catalog, _FuzzyMatcher, get_close_matches
from babel.messages.pofile import write_po


@pytest.mark.parametrize(
    ('word', 'possibilities'),
    [
        ('', []),
        ('', ['']),
        ('', ['a', 'b']),
        ('abcd', ['abce', 'abcf']),
        ('abcd', ['abcf', 'abce']),
        ('abcde', ['abxyz', 'abcyz']),  # Exactly the 0.6 cutoff.
        ('a' * 220 + 'b', ['a' * 220 + 'c', 'a' * 220]),
        ('aaaaabbbbb', ['ab', 'bbaaa', 'aaaaabbbb']),
        ('\ud800\x00é🙂é', ['\ud800\x00é🙂', '\ud800\x00🙂é', 'éé🙂']),
        ('a' * 200, ['a', 'aa', 'aaa']),  # Query counts exceed index counts.
    ],
)
def test_indexed_fuzzy_matches(word, possibilities):
    assert _FuzzyMatcher(possibilities).get_close_matches(word) == get_close_matches(
        word, possibilities, 1,
    )


def test_indexed_fuzzy_matches_exhaustive_short_strings():
    words = [''.join(chars) for size in range(5) for chars in itertools.product('abc', repeat=size)]
    for word in words:
        possibilities = [candidate for candidate in words if candidate != word]
        assert _FuzzyMatcher(possibilities).get_close_matches(word) == get_close_matches(
            word, possibilities, 1,
        )


def test_indexed_fuzzy_matches_generated():
    randomizer = random.Random(9143)
    alphabet = 'abcd eé\x00\udfff🙂'
    for _ in range(100):
        possibilities = [
            ''.join(randomizer.choices(alphabet, k=randomizer.randrange(1, 90)))
            for _ in range(30)
        ]
        matcher = _FuzzyMatcher(possibilities)
        word = randomizer.choice(possibilities)
        for query in (word[1:], word + ' updated', word[::-1]):
            assert matcher.get_close_matches(query) == get_close_matches(query, possibilities, 1)


def test_indexed_fuzzy_matches_string_subclasses():
    calls = []

    class CustomString(str):
        def __iter__(self):
            calls.append('iter')
            return super().__iter__()

    for word, possibilities in [
        (CustomString('changed message'), ['message', 'other message']),
        ('changed message', [CustomString('message'), 'other message']),
    ]:
        calls.clear()
        expected = get_close_matches(word, possibilities, 1)
        expected_calls = calls[:]
        calls.clear()
        assert _FuzzyMatcher(possibilities).get_close_matches(word) == expected
        assert calls == expected_calls


@pytest.mark.parametrize('possibilities', [['a' * 8193], ['a'] * 65537])
def test_indexed_fuzzy_matches_size_limit(possibilities):
    matcher = _FuzzyMatcher(possibilities)
    assert matcher._index is None
    assert matcher.get_close_matches('xyz') == get_close_matches('xyz', possibilities, 1)


def test_indexed_fuzzy_matches_legacy_bit_count(monkeypatch):
    monkeypatch.setattr('babel.messages.catalog._bit_count', lambda value: bin(value).count('1'))
    possibilities = ['repeated repeated letters', 'repeated letters', 'different letters']
    word = 'repeated repeated letters!'
    assert _FuzzyMatcher(possibilities).get_close_matches(word) == get_close_matches(
        word, possibilities, 1,
    )


@pytest.mark.parametrize('keep_user_comments', [False, True])
@pytest.mark.parametrize('no_fuzzy_matching', [False, True])
def test_catalog_update_index_matches_reference(keep_user_comments, no_fuzzy_matching):
    class ReferenceCatalog(Catalog):
        pass

    timestamp = datetime.datetime(2024, 1, 1, tzinfo=datetime.timezone.utc)
    template = Catalog(creation_date=timestamp)
    for index, message_id in enumerate(['a shared message', 'a second message', 'repeated repeated']):
        template.add(message_id + ' changed', locations=[('source.py', index)])
        template.add(message_id + ' changed again', context='new context')
    template.add(('plural item', 'plural items'))
    template.add('context message', context='new context')
    template.add('unchanged message')
    template.add('completely new')

    results = []
    for cls in (Catalog, ReferenceCatalog):
        catalog = cls(locale='de', creation_date=timestamp, revision_date=timestamp)
        for message_id in ['a shared message', 'a second message', 'repeated repeated']:
            catalog.add(message_id, message_id.upper(), user_comments=['keep this'])
        catalog.add(('plural item', 'plural items'), ('Einzahl', 'Mehrzahl'))
        catalog.add('context message', 'Kontext', context='old context')
        catalog.add('unchanged message', 'Unverändert')
        catalog.add('obsolete', 'Veraltet')
        catalog.update(
            template,
            keep_user_comments=keep_user_comments,
            no_fuzzy_matching=no_fuzzy_matching,
        )
        output = BytesIO()
        write_po(output, catalog, include_previous=True)
        results.append(output.getvalue())
    assert results[0] == results[1]


def test_catalog_update_does_not_reuse_index():
    catalog = Catalog(locale='de')
    catalog.add('the original message', 'original translation')
    template = Catalog()
    template.add('the original message changed')
    catalog.update(template)
    catalog['the original message changed'].string = 'modified translation'
    template = Catalog()
    template.add('the original message changed again')
    catalog.update(template)
    assert catalog['the original message changed again'].string == 'modified translation'


def test_catalog_update_subclass_fuzzy_key():
    calls = []

    class CustomCatalog(Catalog):
        def _to_fuzzy_match_key(self, key):
            calls.append(key)
            return super()._to_fuzzy_match_key(key).replace('old', 'new')

    catalog = CustomCatalog()
    catalog.add('old message', 'translation')
    template = Catalog()
    template.add('new message')
    catalog.update(template)
    assert catalog['new message'].string == 'translation'
    assert calls == ['old message', 'new message']
