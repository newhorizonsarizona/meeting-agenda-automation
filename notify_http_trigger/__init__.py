import logging
import os
import requests
import azure.functions as func

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    github_token = os.getenv('GITHUB_AUTH_TOKEN')
    repo_owner = 'newhorizonsarizona'
    repo_name = 'meeting-agenda-automation'
    workflow_filename = 'agenda_notification_test.yml'  # Workflow file name
    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
            name = req_body.get('name')
            logging.info(f"Request received")
        except ValueError as e:
            logging.error(f"Error parsing request body: {str(e)}")
            return func.HttpResponse("Invalid request body", status_code=400)

    workflow_id = get_workflow_id(github_token, repo_owner, repo_name, workflow_filename)
    if not workflow_id:
        logging.error("Workflow not found")
        return func.HttpResponse("Workflow not found", status_code=404)

    url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/actions/workflows/{workflow_id}/dispatches'
    headers = {
        'Authorization': f'token {github_token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    data = {
        'ref': 'main',  # Branch to run the workflow on
    }

    response = requests.post(url, headers=headers, json=data)
    logging.info(f"GitHub API response: {response.status_code}, {response.text}")

    if response.status_code >= 200 and response.status_code < 300:
        return func.HttpResponse(f"Hello {name}, Workflow triggered successfully", status_code=200)
    else:
        logging.error(f"Failed to trigger workflow: {response.json()}")
        return func.HttpResponse(f"Hello {name}, Failed to trigger workflow: {response.json()}", status_code=response.status_code)

def get_workflow_id(github_token, repo_owner, repo_name, workflow_filename):
    url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/actions/workflows'
    headers = {
        'Authorization': f'token {github_token}',
        'Accept': 'application/vnd.github.v3+json'
    }

    response = requests.get(url, headers=headers)
    logging.info(f"GitHub API response for workflow ID: {response.status_code}, {response.text}")

    if response.status_code >= 200 and response.status_code < 300:
        workflows = response.json().get('workflows', [])
        for workflow in workflows:
            if workflow.get('path').endswith(workflow_filename):
                return workflow.get('id')
    else:
        logging.error(f"Failed to fetch workflows: {response.json()}")

    return None
