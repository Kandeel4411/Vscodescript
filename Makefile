update-deps:
	poetry export -f requirements.txt -o requirements.txt --without-hashes
install:
	poetry add $(DEP_NAME) && poetry install $(DEP_NAME)
venv:
	poetry config virtualenvs.create $(PY_VENV)