SHELL := /bin/bash -o pipefail

OUTPUT_PATH ?= ./dist

.PHONY: test test-* format build

format:
	black o365 --line-length 120 
	black agenda_http_trigger --line-length 120 

lint:
	pylint o365 --fail-under 9.30
	pylint agenda_http_trigger --fail-under 9.30

package:
	python setup.py sdist bdist_wheel

test: format lint 
