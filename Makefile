test: import-cldr
	@py.test tests

clean: clean-cldr clean-pyc

import-cldr:
	@./scripts/download_import_cldr.py

clean-cldr:
	@rm babel/localedata/*.dat
	@rm babel/global.dat

clean-pyc:
	@find . -name '*.pyc' -exec rm {} \;

develop:
	@pip install --editable .

tox-test:
	@PYTHONDONTWRITEBYTECODE= tox
	@$(MAKE) clean-pyc

.PHONY: test develop tox-test clean-pyc clean-cldr import-cldr clean
