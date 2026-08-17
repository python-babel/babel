import pickle
import io
import os
import pytest
from babel import localedata

def test_safe_unpickler_rejects_malicious_global():
    class Malicious:
        def __reduce__(self):
            return (os.system, ('echo VULNERABLE',))
            
    buf = io.BytesIO()
    pickle.dump(Malicious(), buf)
    buf.seek(0)
    
    unpickler = localedata._SafeUnpickler(buf)
    with pytest.raises(pickle.UnpicklingError) as excinfo:
        unpickler.load()
    assert 'forbidden' in str(excinfo.value)

def test_safe_unpickler_allows_legit_classes():
    from babel.plural import PluralRule
    from decimal import Decimal
    
    data = {
        'alias': localedata.Alias(('en', 'US')),
        'plural': PluralRule({'one': 'n is 1'}),
        'decimal': Decimal('1.23')
    }
    
    buf = io.BytesIO()
    pickle.dump(data, buf)
    buf.seek(0)
    
    unpickler = localedata._SafeUnpickler(buf)
    loaded = unpickler.load()
    assert isinstance(loaded['alias'], localedata.Alias)
    assert isinstance(loaded['plural'], PluralRule)
    assert isinstance(loaded['decimal'], Decimal)
