import sys
import datetime
import logging

import azure.functions as func
from agenda_creator import AgendaCreator

sys.path.append("../")


def main(mytimer: func.TimerRequest) -> None:
    """Timer trigger for the weekly meeting agenda"""
    utc_timestamp = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info("The timer is past due!")

    logging.info("Python timer trigger function ran at %s", utc_timestamp)
    creator: AgendaCreator = AgendaCreator()
    creator.create()
