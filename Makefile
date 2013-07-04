test: import-cldr
	@python setup.py test

import-cldr:
	@./scripts/download_import_cldr.py

clean-cldr:
	@rm babel/localedata/*.dat

develop:
	@pip install --editable .

tox-test:
	@tox

.PHONY: test develop tox-test
