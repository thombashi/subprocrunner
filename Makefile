PACKAGE := subprocrunner


.PHONY: build
build:
	@make clean
	@tox -e build
	ls -lh dist/*

.PHONY: check
check:
	@tox -e lint
	travis lint
	pip check

.PHONY: clean
clean:
	@tox -e clean

.PHONY: fmt
fmt:
	@tox -e fmt

.PHONY: release
release:
	@tox -e release
	@make clean

.PHONY: setup
setup:
	@pip install --upgrade -e .[test] tox
	pip check
