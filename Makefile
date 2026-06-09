PYTHON ?= python3
UVICORN ?= uvicorn

.PHONY: install run run-ui test lint format

install:
	$(PYTHON) -m pip install -e ".[dev]"

run:
	$(UVICORN) app.main:app --reload --host 0.0.0.0 --port 8080

run-ui:
	streamlit run ui.py --server.port 8501

test:
	pytest

lint:
	ruff check .

format:
	ruff check . --fix
