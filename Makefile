.PHONY: test
test: ARGS ?=
test:
	@pytest --pylint --black --mypy ${ARGS} pymessagebus
