from datetime import datetime
import logging
from zoneinfo import ZoneInfo

import azure.functions as func

from agenda_creator import AgendaCreator

def main(mytimer: func.TimerRequest) -> None:
    """This is a timer based trigger for the the weekly meeting azure function"""
    phx_timestamp = datetime.now(ZoneInfo('Americas/Phoenix')).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function ran at %s', phx_timestamp)
    agenda_creator: AgendaCreator = AgendaCreator()
    agenda_creator.create()
