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
	time python3 ./visit.py -v fake_django/code.py

mrclean:
	@if [[ "$$VIRTUAL_ENV" != "" ]]; then \
		echo "Run 'deactivate' first "; \
	else \
		git clean -fdx; \
		rm -rf venv; \
	fi
