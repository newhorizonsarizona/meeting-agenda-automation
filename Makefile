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

install-tools:
    curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
    sudo sh -c 'echo "deb [arch=amd64] https://packages.microsoft.com/repos/microsoft-ubuntu-$(lsb_release -cs)-prod $(lsb_release -cs) main" > /etc/apt/sources.list.d/dotnetdev.list'
    sudo apt-get update
    sudo apt-get install azure-functions-core-tools-4

az-login:
    az login --use-device-code

az-publish:
    func azure functionapp publish WeeklyMeetingAgenda

az-delete:
    #az functionapp function delete --function-name WeeklyMeetingAgendaApp --name WeeklyMeetingAgenda --resource-group weeklymeetingagenda 

test: format lint 

run: test
     pipenv shell
     source cred.sh
     python cli.py 
