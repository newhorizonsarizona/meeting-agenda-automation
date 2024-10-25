SHELL := /bin/bash -o pipefail

APP_NAME = weeklymeetingagenda
PACKAGE_NAME = $(APP_NAME)notify
FUNCTION_NAME = notify_http_trigger
RESOURCE_GROUP = $(APP_NAME)rs
SUBSCRIPTION_ID = eb792c5c-94c2-48d5-b355-c807ecdbe88e

.PHONY: test test-* format build

format:
	pipenv run black o365 --line-length 120
	pipenv run black commands --line-length 120
	pipenv run black agenda_http_trigger --line-length 120

lint:
	pipenv run pylint o365 --fail-under 9.70
	pipenv run pylint commands --fail-under 10.0
	pipenv run pylint agenda_http_trigger --fail-under 10.0

package:
	python setup.py sdist bdist_wheel

install-tools:
	#curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
	#sudo sh -c 'echo "deb [arch=amd64] https://packages.microsoft.com/repos/microsoft-ubuntu-$(lsb_release -cs)-prod $(lsb_release -cs) main" > /etc/apt/sources.list.d/dotnetdev.list'
	#sudo apt update && sudo apt-get install azure-functions-core-tools-4
	#wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
	#echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
	#sudo apt update && sudo apt install terraform
	wget https://releases.hashicorp.com/terraform/1.8.5/terraform_1.8.5_linux_386.zip && unzip terraform_1.8.5_linux_386.zip && rm -f terraform_1.8.5_linux_386.zip LICENSE.txt

install-python-310:
	sudo apt install python3.10 python3.10-venv python3.10-dev

venv-python-310: install-python-310
	mkdir -p venv && python3.10 -m venv venv/py310

plan-infra:
	./terraform -chdir=./infra/ plan -var client_secret=$(CLIENT_SECRET)

create-infra:
	./terraform -chdir=./infra/ apply -var client_secret=$(CLIENT_SECRET) --auto-approve

destroy-infra:
	./terraform -chdir=./infra/ destroy -var client_secret=$(CLIENT_SECRET) --auto-approve

package-notify-func:
	zip ./$(PACKAGE_NAME).zip $(FUNCTION_NAME)/*

az-login:
	az login --use-device-code

list-app-publish-profiles:
	az functionapp deployment list-publishing-profiles --name $(APP_NAME)  --resource-group $(RESOURCE_GROUP)

deploy-app: az-login package-notify-func
	#func azure functionapp publish $(APP_NAME)
	pushd $(FUNCTION_NAME) && pip install -r requirements.txt && popd
	az functionapp deployment source config-zip --resource-group $(RESOURCE_GROUP) --name $(APP_NAME) --src ./$(PACKAGE_NAME).zip

delete-app: az-login
	az functionapp function delete --function-name $(FUNCTION_NAME) --name $(APP_NAME) --resource-group $(RESOURCE_GROUP) --subscription $(SUBSCRIPTION_ID)

start-app: az-login
	az functionapp start --name $(APP_NAME) --resource-group $(RESOURCE_GROUP) --subscription $(SUBSCRIPTION_ID)

stop-app: az-login
	az functionapp stop --name $(APP_NAME) --resource-group $(RESOURCE_GROUP) --subscription $(SUBSCRIPTION_ID)

test-python: lint

test-agenda-create:
	./nhtm_automation.sh agenda create-weekly-meeting-agenda

test-agenda-notify:
	./nhtm_automation.sh agenda notify-on-teams

test-signup-reminder:
	./nhtm_automation.sh agenda signup-reminder-on-teams

test-planner-create:
	./nhtm_automation.sh planner create-weekly-meeting-plan

test-planner-delete:
	./nhtm_automation.sh planner delete-weekly-meeting-plan

test-sync-signup:
	./nhtm_automation.sh planner sync-signup-with-plan
