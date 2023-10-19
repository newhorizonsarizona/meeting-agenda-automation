import asyncio
import datetime
from logging import Logger
import time
from auth.auth_helper import AuthHelper
from drive.drive_helper import DriveHelper
from user.user_helper import UserHelper
from planner.planner_helper import PlannerHelper
    
group_ids = ['1ab26305-df89-435b-802d-4f223a037771','aa235df6-19fc-4de3-8498-202b5cbe2d15']

class AgendaCreator:
    """This class is used for creating the agenda"""

    def _get_next_meeting_plan(self, graph_client, group_id):
        """Gets plans for the specified group_id"""
        retry_count = 0
        next_meeting_plan = None
        while retry_count < 3:
            try:
                print(f'Getting the plan for next meeting in group: {group_id}')
                plans = asyncio.run(PlannerHelper.get_all_plans(graph_client, group_id))
                if plans and plans.value:
                    for plan in plans.value:
                        if self._next_tuesday_month[:3].lower() in plan.title.lower():
                            print(f'Found next weeks plan {plan}')
                            return plan
            except RuntimeError as e:
                if "Event loop is closed" in str(e):
                    if retry_count < 3:
                        time.sleep(15)
                        retry_count = retry_count + 1
                    else:
                        print(e)
                        break # do something here, like log the error
        return next_meeting_plan

    def _get_next_meeting_bucket(self, graph_client, plan):
        """Gets buckets for the specified plan"""
        retry_count = 0
        next_meeting_bucket = None
        next_tuesday_date = self._next_tuesday_date
        while retry_count < 5:
            try:
                print(f'Getting the bucket for {next_tuesday_date} in plan: {plan.title} ({plan.id})')
                buckets = asyncio.run(PlannerHelper.get_all_buckets(graph_client, plan.id))
                if buckets and buckets.value:
                    for bucket in buckets.value:
                        if self._next_tuesday_date in bucket.name:
                            print(f'Found next weeks bucket {bucket}')
                            return bucket
            except RuntimeError as e:
                if "Event loop is closed" in str(e):
                    if retry_count < 5:
                        time.sleep(15)
                        retry_count = retry_count + 1
                    else:
                        print(e)
                        break # do something here, like log the error
        return next_meeting_bucket

    def _get_next_meeting_tasks(self, graph_client, bucket):
        """Gets tasks in the specified bucket"""
        retry_count = 0
        next_meeting_tasks = None
        while retry_count < 5:
            try:
                print(f'Getting the tasks in bucket: {bucket.name} ({bucket.id})')
                tasks = asyncio.run(PlannerHelper.get_tasks_in_bucket(graph_client, bucket.id))
                if tasks and tasks.value:
                    return tasks
            except RuntimeError as e:
                if "Event loop is closed" in str(e):
                    if retry_count < 5:
                        time.sleep(15)
                        retry_count = retry_count + 1
                    else:
                        print(e)
                        break # do something here, like log the error
        return next_meeting_tasks
 
    def _get_assigned_to_user(self, graph_client, task):
        """Gets assigned to user for task"""
        retry_count = 0
        assigned_to_user = None
        while retry_count < 5:
            try:
                print(f'Getting the assigned to user for task: {task.title}')
                assigned_to_users = list(task.assignments.additional_data.keys())
                if assigned_to_users is not None and len(assigned_to_users) > 0:
                    assigned_to_user_id = list(task.assignments.additional_data.keys())[0]
                    user = asyncio.run(UserHelper.get_user(graph_client, assigned_to_user_id))
                    if user is not None:
                        return user
                else:
                    return assigned_to_user
            except RuntimeError as e:
                if "Event loop is closed" in str(e):
                    if retry_count < 5:
                        time.sleep(15)
                        retry_count = retry_count + 1
                    else:
                        print(e)
                        break # do something here, like log the error
        return assigned_to_user

    def _get_drive(self, graph_client, group_id):
        """Gets the drive for the specified group_id"""
        retry_count = 0
        drive_4_group = None
        while retry_count < 3:
            try:
                print(f'Getting the drive for group: {group_id}')
                drive = asyncio.run(DriveHelper.get_drive(graph_client, group_id))
                if drive:
                    return drive
            except RuntimeError as e:
                if "Event loop is closed" in str(e):
                    if retry_count < 5:
                        time.sleep(15)
                        retry_count = retry_count + 1
                    else:
                        print(e)
                        break # do something here, like log the error
        return drive_4_group


    def _get_weekly_meeting_channel(self, graph_client, drive_id):
        """Gets the drive for the specified group_id"""
        retry_count = 0
        weekly_meeting_channel = None
        while retry_count < 3:
            try:
                print(f'Getting the weekly meeting channel for drive: {drive_id}')
                drive_item = asyncio.run(DriveHelper.get_drive_item(graph_client, drive_id, 3)) # 3 = Weekly Meeting Channel id
                if drive_item:
                    return drive_item
            except RuntimeError as e:
                if "Event loop is closed" in str(e):
                    if retry_count < 5:
                        time.sleep(15)
                        retry_count = retry_count + 1
                    else:
                        print(e)
                        break # do something here, like log the error
        return weekly_meeting_channel

    def create(self):
        """Get the planner tasks for next meeting"""
        print('Creating agenda')
        try:
            graph_client = AuthHelper.graph_service_client()
            for group_id in group_ids:
                drive = self._get_drive(graph_client, group_id)
                print(f'Drive id: {drive.id}')
                drive_item = self._get_weekly_meeting_channel(graph_client, drive.id)
                print(f'Drive item: {drive_item.name}')
                plan = self._get_next_meeting_plan(graph_client, group_id)
                if plan is None:
                    print('No matching plan found for next the meeting next week')
                    exit(1)
                bucket = self._get_next_meeting_bucket(graph_client, plan)
                if bucket is None:
                    print('No matching bucket found for next the meeting next week')
                    exit(1)
                tasks = self._get_next_meeting_tasks(graph_client, bucket)
                if tasks is None:
                    print('No matching tasks found for next the meeting next week')
                    exit(1)
                for task in tasks.value:
                    assigned_to_user = self._get_assigned_to_user(graph_client, task)
                    if assigned_to_user is not None:
                        print(f'{task.title}, due {task.due_date_time} is assigned to {assigned_to_user.display_name}')
                print(f'Successfully created the agenda for the next meeting on {self._next_tuesday_date}')
                return
        except RuntimeError as e:
            print(f'Error creating agenda. {e}')
                                
        print('No matching plan or buckets were found for next the meeting next week')
        exit(1)


    @property
    def _next_tuesday(self):
        """Return the date time for next Tuesday"""
        today = datetime.date.today()
        next_tuesday = today + datetime.timedelta((1-today.weekday()) % 7)
        return next_tuesday

    @property
    def _next_tuesday_date(self):
        """Return the date time string in yyyyMMdd format for next Tuesday"""
        return self._next_tuesday.strftime('%Y%m%d')

    @property
    def _next_tuesday_month(self):
        """Return the month string for next Tuesday"""
        return self._next_tuesday.strftime('%B')

agenda_creator: AgendaCreator = AgendaCreator()
agenda_creator.create()
