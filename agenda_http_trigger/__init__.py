import logging
import os
import asyncio
import time

import azure.functions as func

from o365.agenda_creator import AgendaCreator


async def main(req: func.HttpRequest) -> func.HttpResponse:
    """Main entry point to the function"""
    logging.info("Python HTTP trigger function processed a request.")

    function_key = os.environ["FUNCTION_KEY"]
    key = req.params.get("key")
    name = req.params.get("name")
    if not key:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            key = req_body.get("key")
            name = req_body.get("name")

    if key != function_key:
        return func.HttpResponse("Unauthorized", status_code=401)

    response_data = "".join([data async for data in create_agenda(name)])
    response = func.HttpResponse(body=response_data, mimetype="text/event-stream")
    return response


async def create_agenda(name: str = "NHTM"):
    """Function that triggers the agenda creation asunchronously"""
    creator: AgendaCreator = AgendaCreator()
    status = creator.create()
    count = 0
    while True:
        msg = f"Hello {name}, The agenda creation has started.."
        if count > 0:
            msg = "Creating agenda.."
            if status == "Success":
                msg = "Creation of the agenda was successful!"
            if status == "Failure":
                msg = "Creation of the agenda failed!"
        if status == "Success" or status == "Failure":
            break
        time.sleep(10)  # Send update every 10 seconds
        yield f"data: {msg}\n\n"
        count = count + 1


async def generate_response(generator):
    """Iterate through the responses"""
    async for item in generator:
        yield item


# GET https://login.microsoftonline.com/9add987e-b316-43b4-8750-4007763832b0/oauth2/v2.0/authorize?
# client_id=68e11217-f842-4df4-8720-75a08c58f491&response_type=code
# &redirect_uri=https%3A%2F%2Fweeklymeetingagenda.azurewebsites.net%2F&response_mode=query
# &scope=user.read&state=12345
