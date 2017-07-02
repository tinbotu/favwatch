.PHONY: test clean setup deploy status lint

run:
	./bin/python favwatch.py

test:
	rm -f tmp.sqlite
	./bin/python tests.py

clean:
	find . -name "*.py[co]" -delete
	rm -rf *sqlite* __pycache__ .mypy_cache

setup:
	python3 -m venv .
	./bin/pip install -r requirements.txt

update_packages:
	./bin/pip install -r requirements.txt

lint:
	./bin/flake8 favwatch.py
	./bin/mypy favwatch.py
