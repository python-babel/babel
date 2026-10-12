test: import-cldr
	python -X utf8 ${PYTHON_TEST_FLAGS} -m pytest ${PYTEST_FLAGS}

clean: clean-cldr clean-pyc

import-cldr:
	python scripts/download_import_cldr.py

clean-cldr:
	rm -f babel/locale-data/*.dat
	rm -f babel/global.dat

clean-pyc:
	find . -name '*.pyc' -exec rm {} \;
	find . -name '__pycache__' -type d | xargs rm -rf

develop:
	pip install --editable .

tox-test:
	tox

update-gha:
	uvx gha-tools@latest autoupdate --pin all -s specific --first-party-version-strategy=major --write .github/workflows/

.PHONY: test develop tox-test clean-pyc clean-cldr import-cldr clean update-gha
