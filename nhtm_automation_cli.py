import click

from commands.agenda import agenda_cmd
from commands.planner import planner_cmd

__author__ = """Anand Vijayachandran"""
__email__ = "avijaychandran@newhorizonsarizona.org"
__version__ = "0.1.0"


@click.group()
def nhtm_automation():
    """NHTM Automation CLI"""

# Add commands
nhtm_automation.add_command(agenda_cmd)
nhtm_automation.add_command(planner_cmd)

if __name__ == "__main__":
    # prog_name allows to override displayed application name: https://click.palletsprojects.com/en/5.x/api/#commands
    # Disable false positive 'Unexpected keyword argument' error for this invocation
    # pylint: disable=E1123
    nhtm_automation(prog_name="nhtm_automation.sh")
