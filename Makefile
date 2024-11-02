all: test

venv:
	virtualenv .venv

deps:
	@if [[ "$$VIRTUAL_ENV" != "" ]]; then \
		pip install -r requirements.txt; \
	else \
		echo "Run 'source .venv/bin/activate' first "; \
	fi

test:
	python3 ./visit.py
