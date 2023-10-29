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

    weekly_meeting_doc_lib_id :  str = '01FL2JKR56Y2GOVW7725BZO354PWSELRRZ'

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

    def _get_children_for_path(self, graph_client, drive_id, children, path):
        """Gets the children for the specified path"""
        retry_count = 0
        children_for_path = None
        while retry_count < 3:
            try:
                #print(f'Getting the children for path: {path}')
                path_items = path.split('/')
                if path_items:
                    for child in children.value:
                        print(f'Getting the child: {child.name}, matching with path {path_items[0]}')
                        if child.name == path_items[0]:
                            print(f'Getting the children for path: {child.name}')
                            children = asyncio.run(DriveHelper.get_children_by_item(graph_client, drive_id, child.id))
                            if len(path_items) > 1:
                                children = self._get_children_for_path(graph_client, drive_id, children, path_items[1])
                            #print(children)
                return children
            except RuntimeError as e:
                if "Event loop is closed" in str(e):
                    if retry_count < 5:
                        time.sleep(15*retry_count)
                        retry_count = retry_count + 1
                    else:
                        print(e)
                        break # do something here, like log the error
        return children_for_path

    def _get_drive_item_id_for_path(self, graph_client, drive_id, item_id, path):
        """Gets the drive item id for the specified path"""
        retry_count = 0
        drive_item_id = None
        while retry_count < 3:
            try:
                #print(f'Getting the children for path: {path}')
                path_items = path.split('/')
                if path_items:
                    children = asyncio.run(DriveHelper.get_children_by_item(graph_client, drive_id, item_id))
                    for child in children.value:
                        print(f'Getting the child: {child.name}, matching with path {path_items[0]}')
                        if child.name == path_items[0]:
                            print(f'The item id for {child.name} is {child.id}')
                            if len(path_items) > 1:
                                drive_item_id = self._get_drive_item_id_for_path(graph_client, drive_id, child.id, path_items[1])
                            drive_item_id = child.id
                        return drive_item_id
            except RuntimeError as e:
                if "Event loop is closed" in str(e):
                    if retry_count < 5:
                        time.sleep(15*retry_count)
                        retry_count = retry_count + 1
                    else:
                        print(e)
                        break # do something here, like log the error
        return drive_item_id

    def _get_drive_item_id(self, graph_client, drive_id, path):
        """Gets the drive for the specified group_id"""
        retry_count = 0
        drive_item_id = None
        while retry_count < 3:
            try:
                print(f'Getting the weekly meeting channel children for drive: {drive_id}')
                root_children = asyncio.run(DriveHelper.get_children_by_path(graph_client, drive_id)) # 3 = Weekly Meeting Channel id
                if root_children and root_children.value:
                    for root_child in root_children.value:
                        path_items = path.split('/')
                        if path_items[0] == root_child.name:
                            print(f'Getting the item id for path: {path}')
                            drive_item_id = root_child.id
                            if len(path_items) > 1:
                                drive_item_id = self._get_drive_item_id_for_path(graph_client, drive_id, drive_item_id, path)
                            return drive_item_id
            except RuntimeError as e:
                if "Event loop is closed" in str(e):
                    if retry_count < 5:
                        time.sleep(15*retry_count)
                        retry_count = retry_count + 1
                    else:
                        print(e)
                        break # do something here, like log the error
        return drive_item_id
    
    def create(self):
        """Get the planner tasks for next meeting"""
        print('Creating agenda')
        try:
            graph_client = AuthHelper.graph_service_client()
            drive = self._get_drive(graph_client, 'aa235df6-19fc-4de3-8498-202b5cbe2d15')
            print(f'Drive id: {drive.id}')
            wmc_drive_item_id = self._get_drive_item_id(graph_client, drive.id, 'Weekly Meeting Channel')
            print(f'Weekly Meeting Channel Drive Item Id: {wmc_drive_item_id}')
            ma_drive_item_id = self._get_drive_item_id(graph_client, drive.id, 'Meeting Automation')
            print(f'Meeting Automation Drive Item Id: {ma_drive_item_id}')
            for group_id in group_ids:
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
