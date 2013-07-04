test:
	python setup.py test

develop:
	pip install --editable .

tox-test:
	@tox

.PHONY: test develop tox-test
