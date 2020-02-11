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
	@tox -e lint
	travis lint

.PHONY: clean
clean:
	@tox -e clean

.PHONY: fmt
fmt:
	@tox -e fmt

.PHONY: release
release:
	@python setup.py release --sign
	@make clean

.PHONY: setup
setup:
	@pip install --upgrade .[dev] tox
