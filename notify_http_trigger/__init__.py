import logging
import os

import requests

import azure.functions as func

# Load GitHub token from environment variable
GITHUB_TOKEN = os.getenv('GITHUB_AUTH_TOKEN')
REPO_OWNER = 'newhorizonsarizona'
REPO_NAME = 'meeting-agenda-automation'
WORKFLOW_FILENAME = 'agenda_notification_test.yml'  # Filename of the workflow

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('name')

    if name.upper() in ['VPE','OFFICER','ANAND']:
        auth_code = req.params.get('code')
        if auth_code[:2] == '0.':
            url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/workflows'
            headers = {
                'Authorization': f'token {GITHUB_TOKEN}',
                'Accept': 'application/vnd.github.v3+json'
            }

            response = requests.get(url, headers=headers)
            workflow_id = None
            if response.status_code >= 200 and response.status_code < 300:
                workflows = response.json().get('workflows', [])
                for workflow in workflows:
                    if workflow.get('path').endswith(WORKFLOW_FILENAME):
                        workflow_id = workflow.get('id')
            if workflow_id is None:
                return func.HttpResponse(f"Hello, {name}. \
                                        [WARNING] Your message was received and \
                                         there was an error while sending the notification.")
            
            url += f'/{workflow_id}/dispatches'
            data = {
                'ref': 'main',  # The branch to run the workflow on
                'inputs': {
                    'user_auth_code': auth_code
                }
            }

            response = requests.post(url, headers=headers, json=data)

            if response.status_code >= 200 and response.status_code < 300:
                return func.HttpResponse(f"Hello, {name}. \
                                        [SUCCESS] Your message was received and \
                                         the agenda notification shall be sent out shortly.")
            else:
                return func.HttpResponse(f"Hello, {name}. \
                                        [ERROR] Your message was received and \
                                         there was an error while sending the notification.")
        return func.HttpResponse(f"Hello, {name},\
                                     [NOOP] This HTTP triggered function executed successfully and\
                                        no operation was performed.")
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a valid name in the query string.",
             status_code=200
        )
