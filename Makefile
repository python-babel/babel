test: import-cldr
	python3 ${PYTHON_TEST_FLAGS} -m pytest ${PYTEST_FLAGS}

test-env:
	virtualenv test-env
	test-env/bin/pip install pytest
	test-env/bin/pip install --editable .

clean-test-env:
	rm -rf test-env

standalone-test: import-cldr test-env
	test-env/bin/pytest tests ${PYTEST_FLAGS}

clean: clean-cldr clean-pyc clean-test-env

import-cldr:
	python3 scripts/download_import_cldr.py

clean-cldr:
	rm -f babel/locale-data/*.dat
	rm -f babel/global.dat

clean-pyc:
	find . -name '*.pyc' -exec rm {} \;
	find . -name '__pycache__' -type d | xargs rm -rf

develop:
	pip install --editable .

tox-test: import-cldr
	tox

.PHONY: test develop tox-test clean-pyc clean-cldr import-cldr clean clean-test-env standalone-test
