from datetime import date, timedelta
import time
from loguru import logger
from time import strftime, strptime
from o365.auth.auth_helper import AuthHelper
from o365.planner.planner_helper import PlannerHelper
from o365.util.constants import Constants
from o365.util.date_util import DateUtil


class WeeklyMeetingPlanner:
    """This class is used to create the weekly meeting plan"""

    _graph_client = None
    _next_month_first_day: date
    _group_id: str
    _next_months_meeting_dates: list

    def __init__(self, next_month_first_day: date = None):
        self._graph_client = AuthHelper.graph_service_client_with_adapter()
        self._group_id = Constants.GROUP_IDS[0]
        date_util = DateUtil()
        if next_month_first_day is None:
            self._next_month_first_day = date_util.next_month_first_day
            self._next_months_meeting_dates = date_util.all_tuesdays(True)
        else:
            self._next_month_first_day = next_month_first_day
            self._next_months_meeting_dates = DateUtil(
                f"{self._next_month_first_day.month}/{self._next_month_first_day.day}/{self._next_month_first_day.year}"
            ).all_tuesdays()

    def create_plan(self, plan_name: str):
        """Creates weekly meeting plan with the specified name"""
        logger.info(f"Creating weekly meeting plan with name {plan_name}")
        plan = PlannerHelper.get_plan_by_name(self._graph_client, self._group_id, plan_name)
        if plan is not None:
            logger.info(f"Found plan with name {plan_name} and id {plan.id}")
            return plan
        return PlannerHelper.create_plan_with_name(self._graph_client, self._group_id, plan_name)

    def create_buckets(self, plan_id: str):
        """Creates the weekly meeting buckets"""
        logger.info(f"Creating weekly meeting buckets {self._next_months_meeting_dates} in plan {plan_id}")
        order_hint = " !"
        for next_meeting_date in self._next_months_meeting_dates:
            bucket_name = next_meeting_date.strftime(f"%Y%m%d Meeting Roles")
            bucket = PlannerHelper.get_bucket_by_name(self._graph_client, plan_id, bucket_name)
            if bucket is not None:
                logger.info(f"Found bucket with name {bucket_name} and id {bucket.id}")
                continue
            PlannerHelper.create_bucket_with_name(self._graph_client, plan_id, bucket_name, order_hint)
            order_hint += order_hint

    def populate_tasks_in_buckets_from_template(self, plan_id: str):
        """Populates the tasks in weekly meeting plan buckets from weekly meeting meeting template plan"""
        logger.info(f"Populating weekly meeting tasks from template in plan {plan_id}")
        order_hint = " !"
        template_bucket = PlannerHelper.get_bucket_by_name(
            self._graph_client, Constants.WEEKLY_MEETING_TEMPLATE_PLAN_ID, "YYYYMMDD Meeting Roles"
        )
        tasks_in_template_bucket = PlannerHelper.fetch_tasks_in_bucket(self._graph_client, template_bucket.id)
        buckets_4_plan = PlannerHelper.fetch_all_buckets(self._graph_client, plan_id)
        bucket_details_4_plan = {}
        for bucket_4_plan in buckets_4_plan:
            bucket_details_4_plan.update({bucket_4_plan.id: bucket_4_plan.name})
        logger.debug(f"Bucket details for plan: {bucket_details_4_plan}")
        for bucket_id, bucket_name in bucket_details_4_plan.items():
            if bucket_name == "To do":
                # PlannerHelper.delete_bucket_by_name(self._graph_client, plan_id, bucket_name)
                continue
            tasks_in_bucket_4_plan = PlannerHelper.fetch_tasks_in_bucket(self._graph_client, bucket_id)
            for task_in_template_bucket in tasks_in_template_bucket:
                if tasks_in_bucket_4_plan:
                    found_task = False
                    for task_in_bucket_4_plan in tasks_in_bucket_4_plan:
                        if task_in_bucket_4_plan.title == task_in_template_bucket.title:
                            logger.info(f"Found task with name {task_in_bucket_4_plan.title} in bucket id {bucket_id}")
                            found_task = True
                            break
                    if found_task:
                        continue
                logger.debug(f"Creating task from template: {task_in_template_bucket}")
                PlannerHelper.create_task_in_bucket(
                    self._graph_client,
                    bucket_id,
                    plan_id,
                    task_in_template_bucket.title,
                    order_hint,
                )
                # TODO: Update task with due date and description
                # strptime(bucket_name.split()[0], "%Y%m%d"),
            del tasks_in_bucket_4_plan
