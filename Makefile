test: import-cldr
	@PYTHONWARNINGS=default python ${PYTHON_TEST_FLAGS} -m pytest

test-cov: import-cldr
	@PYTHONWARNINGS=default python ${PYTHON_TEST_FLAGS} -m pytest --cov=babel

test-env:
	@virtualenv test-env
	@test-env/bin/pip install pytest
	@test-env/bin/pip install --editable .

clean-test-env:
	@rm -rf test-env

standalone-test: import-cldr test-env
	@test-env/bin/py.test tests

clean: clean-cldr clean-pyc clean-test-env

import-cldr:
	@python scripts/download_import_cldr.py

clean-cldr:
	@rm -f babel/locale-data/*.dat
	@rm -f babel/global.dat

clean-pyc:
	@find . -name '*.pyc' -exec rm {} \;
	@find . -name '__pycache__' -type d | xargs rm -rf

develop:
	@pip install --editable .

tox-test: import-cldr
	@tox

upload-docs:
	$(MAKE) -C docs html dirhtml latex
	$(MAKE) -C docs/_build/latex all-pdf
	cd docs/_build/; mv html babel-docs; zip -r babel-docs.zip babel-docs; mv babel-docs html
	rsync -a docs/_build/dirhtml/ pocoo.org:/var/www/babel.pocoo.org/docs/
	rsync -a docs/_build/latex/Babel.pdf pocoo.org:/var/www/babel.pocoo.org/docs/babel-docs.pdf
	rsync -a docs/_build/babel-docs.zip pocoo.org:/var/www/babel.pocoo.org/docs/babel-docs.zip

release: import-cldr
	python scripts/make-release.py

.PHONY: test develop tox-test clean-pyc clean-cldr import-cldr clean release upload-docs clean-test-env standalone-test
