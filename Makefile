.PHONY: install test lint build-site serve

install:
	pip install -e ".[dev]"

test:
	pytest -v

lint:
	ruff check .

build-site:
	python3 scripts/build_site.py

serve: build-site
	python3 -m http.server --directory site 8000
