import datetime
from loguru import logger
import click
from o365.util.date_util import DateUtil
from o365.weekly_meeting_planner import WeeklyMeetingPlanner


@click.group(name="planner")
def planner_cmd():
    """The planner command"""


@planner_cmd.command()
@click.option("--name", default="World", help="The name to greet.")
def sync_signup_with_plan(month, year):
    """The planner command to sync the weekly meeting signup with the weekly meeting plan tasks"""
    logger.info(f"Syncing weekly meeting signup, with plan for {month}-{year}!")


@planner_cmd.command()
@click.option("--month", default=None, help="Month (in MMM format e.g. May) for which the plan is being created.")
@click.option("--year", default=None, help="Year (in yyyy format e.g. 2024) for which the plan is being created.")
def create_weekly_meeting_plan(month, year):
    """The planner command to create the weekly meeting plan, buckets and tasks"""
    date_util = DateUtil()
    next_tuesday_date = date_util.next_tuesday_date_us
    if month is None:
        month = DateUtil(next_tuesday_date).next_tuesday_month
    if year is None:
        year = DateUtil(next_tuesday_date).next_tuesday_year
    logger.info(f"Creating plan for month, {month}-{year}!")
    next_month_first_day = datetime.datetime.strptime(f"01 {month}, {year}", "%d %b, %Y")
    weekly_meeting_planner = WeeklyMeetingPlanner(next_month_first_day)
    next_months_plan = weekly_meeting_planner.create_plan(f"{month} - Weekly Meeting Signup")
    weekly_meeting_planner.create_buckets(next_months_plan.id)
    weekly_meeting_planner.populate_tasks_in_buckets_from_template(next_months_plan.id)


@planner_cmd.command()
@click.option("--month", default=None, help="Month for which the plan is being created.")
def delete_weekly_meeting_plan(month):
    """The planner command to delete the weekly meeting plan"""
    logger.info(f"Deleting plan for month, {month}!")
