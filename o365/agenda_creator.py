import asyncio
import datetime
from logging import Logger
import time
from auth.auth_helper import AuthHelper
from planner.planner_helper import PlannerHelper
    
group_ids = ['1ab26305-df89-435b-802d-4f223a037771','aa235df6-19fc-4de3-8498-202b5cbe2d15']

class AgendaCreator:
    """This class is used for creating the agenda"""

    def _get_plans(self, group_id):
        """Gets plans for the specified group_id"""
        retry_count = 0
        while retry_count < 3:
            try:
                print(f'Getting the plans for group: {group_id}')
                plans = asyncio.run(PlannerHelper.get_all_plans(group_id))
                return plans
            except RuntimeError as e:
                if "Event loop is closed" in str(e):
                    if retry_count < 3:
                        time.sleep(5)
                        retry_count = retry_count + 1
                    else:
                        break # do something here, like log the error

    def _get_buckets(self, plan):
        """Gets buckets for the specified plan"""
        retry_count = 0
        while retry_count < 3:
            try:
                print(f'Getting the buckets for plan: {plan.title} ({plan.id})')
                buckets = asyncio.run(PlannerHelper.get_all_buckets(plan.id))
                return buckets
            except RuntimeError as e:
                if "Event loop is closed" in str(e):
                    if retry_count < 3:
                        time.sleep(5)
                        retry_count = retry_count + 1
                    else:
                        break # do something here, like log the error

    def _get_tasks_in_bucket(self, bucket: str):
        """Gets tasks in the specified bucket"""
        retry_count = 0
        while retry_count < 3:
            try:
                print(f'Getting the tasks in bucket: {bucket.name} ({bucket.id})')
                buckets = asyncio.run(PlannerHelper.get_tasks_in_bucket(bucket.id))
                return buckets
            except RuntimeError as e:
                if "Event loop is closed" in str(e):
                    if retry_count < 3:
                        time.sleep(5)
                        retry_count = retry_count + 1
                    else:
                        break # do something here, like log the error

    def _next_tuesday(self):
        """Return the date time string for next Tuesday"""
        today = datetime.date.today()
        next_tuesday = today + datetime.timedelta((1-today.weekday()) % 7)
        return next_tuesday.strftime('%Y%m%d')

    def next_meeting_tasks(self):
        """Get the planner tasks for next meeting"""
        print('Creating agenda')
        for group_id in group_ids:
            plans = self._get_plans(group_id)
            print(plans)
            if plans and plans.value:
                for plan in plans.value:
                    buckets = self._get_buckets(plan)
                    if buckets and buckets.value:
                        for bucket in buckets.value:  
                            next_tuesday = self._next_tuesday()
                            if next_tuesday in bucket.name:
                                tasks = self._get_tasks_in_bucket(bucket)
                                if tasks and tasks.value:
                                    for task in tasks.value:
                                        print(f'{task.title}, due {task.due_date_time} is assigned to {task.assignments}')

agenda_creator: AgendaCreator = AgendaCreator()
agenda_creator.next_meeting_tasks()
