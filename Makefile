SHELL := /bin/bash -o pipefail

OUTPUT_PATH ?= ./dist

.PHONY: test test-* format build

format:
	black o365
	black agenda_http_trigger

lint:
	pylint o365
	black agenda_http_trigger

package:
	python setup.py sdist bdist_wheel

test: format lint 
