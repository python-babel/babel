test: import-cldr
	@py.test tests

import-cldr:
	@./scripts/download_import_cldr.py

clean-cldr:
	@rm babel/localedata/*.dat
	@rm babel/global.dat

develop:
	@pip install --editable .

tox-test:
	@PYTHONDONTWRITEBYTECODE= tox

.PHONY: test develop tox-test
