import logging

import azure.functions as func

from o365.agenda_creator import AgendaCreator


def main(req: func.HttpRequest) -> func.HttpResponse:
    """Main entry point to the function"""
    logging.info("Python HTTP trigger function processed a request.")

    name = req.params.get("name")
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get("name")

    if name:
        creator: AgendaCreator = AgendaCreator()
        creator.create()
        return func.HttpResponse(f"Hello, {name}. The Agenda HTTP triggered function executed successfully.")

    return func.HttpResponse(
        "This HTTP triggered function executed successfully. \
        Pass a name in the query string or in the request body for a personalized response.",
        status_code=200,
    )


# GET https://login.microsoftonline.com/9add987e-b316-43b4-8750-4007763832b0/oauth2/v2.0/authorize?
# client_id=68e11217-f842-4df4-8720-75a08c58f491&response_type=code
# &redirect_uri=https%3A%2F%2Fweeklymeetingagenda.azurewebsites.net%2F&response_mode=query
# &scope=user.read&state=12345
