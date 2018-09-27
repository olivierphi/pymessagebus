PYTHON ?= python3.7
PYPIRC ?= ~/.pypirc

.PHONY: test
test: ARGS ?=
test:
	@ PYTHONPATH=src/ MYPYPATH=src/ pytest --pylint --black --mypy ${ARGS}

.PHONY: package-clean
package-clean:
	rm -rf .cache/ .eggs/ build/ dist/ **/*.egg-info

.PHONY: package-build
package-build: package-clean
	${PYTHON} setup.py bdist_wheel

# The "upload" tasks require a "~/.pypicrc" file
# @link https://docs.python.org/3/distutils/packageindex.html#pypirc
# @link https://packaging.python.org/guides/using-testpypi/#setting-up-testpypi-in-pypirc
.PHONY: package-upload-test
package-upload-test: package-build
	${PYTHON} -m twine upload --config-file ${PYPIRC} --repository pypitest dist/*	
