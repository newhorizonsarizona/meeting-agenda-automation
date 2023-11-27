import sys
import logging

import azure.functions as func

sys.path.append('./')
sys.path.append('./o365')

from o365.agenda_creator import AgendaCreator

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Agenda Creator HTTP trigger function processed a request.')

    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('name')

    if name:
        return func.HttpResponse(f"Hello, {name}. Triggerring the agenda creation.")
        creator: AgendaCreator = AgendaCreator()
        creator.create()
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )
