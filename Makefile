.PHONY: test
test:
	@pytest --pylint --black --mypy pymessagebus
