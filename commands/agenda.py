import click
from loguru import logger
from o365.agenda_creator import AgendaCreator
from o365.agenda_notifier import AgendaNotifier


@click.group(name="agenda")
def agenda_cmd():
    """The agenda command"""


@agenda_cmd.command()
def create_weekly_meeting_agenda():
    """The agenda command to create the weekly meeting agenda"""
    logger.info("Creating the weekly meeting agenda!")
    AgendaCreator().create()


@agenda_cmd.command()
def notify_on_teams():
    """The agenda command to send the teams notification"""
    logger.info("Sending the teams notification!")
    AgendaNotifier().send()
