PYTHON_BINS ?= ./.venv/bin/
PYPIRC ?= ~/.pypirc

.PHONY: install
install: .venv
	${PYTHON_BINS}poetry install

.PHONY: black
black: .venv
	@${PYTHON_BINS}black src/

.PHONY: pylint
pylint: .venv
	@ PYTHONPATH=${PWD}/src/ ${PYTHON_BINS}pylint pymessagebus

.PHONY: mypy
mypy: .venv
	@ PYTHONPATH=${PWD}/src/ ${PYTHON_BINS}mypy src/

.PHONY: test
test: ARGS ?=
test:
	@ PYTHONPATH=${PWD}/src/ ${PYTHON_BINS}pytest ${ARGS}

.PHONY: package-clean
package-clean:
	rm -rf .cache/ .eggs/ build/ dist/ **/*.egg-info

.PHONY: package-build
package-build: package-clean
	${PYTHON_BINS}python setup.py bdist_wheel

# The "upload" tasks require a "~/.pypicrc" file
# @link https://packaging.python.org/specifications/pypirc/
.PHONY: package-upload-test
package-upload-test: package-build
	${PYTHON_BINS}python -m twine upload --config-file ${PYPIRC} --repository testpypi dist/*

.venv:
	python3 -m venv .venv
	./.venv/bin/pip install poetry
