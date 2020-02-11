PACKAGE := subprocrunner


.PHONY: build
build:
	@make clean
	@python setup.py sdist bdist_wheel
	@twine check dist/*
	@python setup.py clean --all
	ls -lh dist/*

.PHONY: check
check:
	python setup.py check
	codespell $(PACKAGE) examples test README.rst -q 2 --check-filenames --ignore-words-list followings
	pylama

.PHONY: clean
clean:
	@tox -e clean

.PHONY: fmt
fmt:
	@black $(CURDIR)
	@autoflake --in-place --recursive --remove-all-unused-imports --exclude "__init__.py" .
	@isort --apply --recursive

.PHONY: release
release:
	@python setup.py release --sign
	@make clean

.PHONY: setup
setup:
	@pip install --upgrade .[dev] tox
