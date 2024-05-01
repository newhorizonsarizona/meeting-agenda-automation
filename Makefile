SHELL := /bin/bash -o pipefail

OUTPUT_PATH ?= ./dist

.PHONY: test test-* format build

format:
	pipenv run black o365 --line-length 120
	pipenv run black commands --line-length 120
	pipenv run black agenda_http_trigger --line-length 120

lint:
	pipenv run pylint o365 --fail-under 9.30
	pipenv run pylint commands --fail-under 9.30
	pipenv run pylint agenda_http_trigger --fail-under 9.30

package:
	python setup.py sdist bdist_wheel

install-tools:
	curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
	sudo sh -c 'echo "deb [arch=amd64] https://packages.microsoft.com/repos/microsoft-ubuntu-$(lsb_release -cs)-prod $(lsb_release -cs) main" > /etc/apt/sources.list.d/dotnetdev.list'
	sudo apt-get update
	sudo apt-get install azure-functions-core-tools-4

az-login:
	az login --use-device-code

az-publish: az-login
	func azure functionapp publish WeeklyMeetingAgenda

az-delete: az-login
	az functionapp function delete --function-name WeeklyMeetingAgendaApp --name WeeklyMeetingAgenda --resource-group weeklymeetingagenda

test-python: format lint

test-agenda-create:
	./nhtm_automation.sh agenda create-weekly-meeting-agenda

test-agenda-notify:
	./nhtm_automation.sh agenda notify-on-teams

test-planner-create:
	./nhtm_automation.sh planner create-weekly-meeting-plan

debug:
	pipenv shell "source cred.sh && export LOGURU_LEVEL=DEBUG && python cli.py"

run:
	pipenv shell "source cred.sh && export LOGURU_LEVEL=INFO && python cli.py"