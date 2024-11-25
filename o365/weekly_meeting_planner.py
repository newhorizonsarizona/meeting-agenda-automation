import asyncio
import json
from datetime import date, datetime
import time
from loguru import logger
from msgraph.generated.models.planner_task import PlannerTask
from msgraph.generated.models.planner_assignments import PlannerAssignments
from o365.auth.auth_helper import AuthHelper
from o365.exception.agenda_exception import AgendaException
from o365.planner.planner_helper import PlannerHelper
from o365.user.user_helper import UserHelper
from o365.util.constants import Constants
from o365.util.date_util import DateUtil
from o365.graph.graph_helper import GraphHelper


class WeeklyMeetingPlanner:
    """This class is used to create the weekly meeting plan"""

    _graph_client = None
    _next_month_first_day: date
    _group_id: str
    _next_months_meeting_dates: list
    _next_tuesday: datetime
    _next_tuesday_date: str

    def __init__(self, next_month_first_day: date = None):
        self._graph_client = AuthHelper.graph_service_client_with_adapter()
        self._group_id = Constants.GROUP_IDS[0]
        date_util = DateUtil()
        self._next_tuesday = date_util.next_tuesday
        self._next_tuesday_date = date_util.next_tuesday_date
        if next_month_first_day is None:
            self._next_month_first_day = date_util.next_month_first_day
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
            bucket_name = next_meeting_date.strftime("%Y%m%d Meeting Roles")
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
        tasks_in_template_bucket = []
        tmp_tasks_in_template_bucket = self._fetch_tasks_in_bucket(template_bucket.id)
        for tmp_task_in_template_bucket in tmp_tasks_in_template_bucket:
            tasks_in_template_bucket.append(
                {"id": tmp_task_in_template_bucket.id, "title": tmp_task_in_template_bucket.title}
            )
        buckets_4_plan = PlannerHelper.fetch_all_buckets(self._graph_client, plan_id)
        bucket_details_4_plan = {}
        for bucket_4_plan in buckets_4_plan:
            bucket_details_4_plan.update({bucket_4_plan.id: {"bucket_name": bucket_4_plan.name, "tasks_info": []}})
        logger.debug(f"Bucket details for plan: {bucket_details_4_plan}")
        for bucket_id, bucket_details in bucket_details_4_plan.items():
            if bucket_details["bucket_name"] == "To do":
                # PlannerHelper.delete_bucket_by_name(self._graph_client, bucket_id, etag)
                continue
            tasks_in_bucket_4_plan = self._fetch_tasks_in_bucket(bucket_id)
            logger.debug(f"Tasks in template bucket: {tasks_in_template_bucket}")
            template_tasks_index = len(tasks_in_template_bucket) - 1
            # Preserve order of tasks by looping in reverse with the provided order hint
            while template_tasks_index >= 0:
                task_in_template_bucket = tasks_in_template_bucket[template_tasks_index]
                if tasks_in_bucket_4_plan:
                    found_task = False
                    for task_in_bucket_4_plan in tasks_in_bucket_4_plan:
                        if task_in_bucket_4_plan.title == task_in_template_bucket["title"]:
                            logger.info(f"Found task with name {task_in_bucket_4_plan.title} in bucket id {bucket_id}")
                            found_task = True
                            bucket_details["tasks_info"].append(
                                {"id": task_in_bucket_4_plan.id, "title": task_in_bucket_4_plan.title}
                            )
                            break
                    if found_task:
                        template_tasks_index -= 1
                        continue
                logger.debug(f"Creating task from template: {task_in_template_bucket}")
                new_task = PlannerHelper.create_task_in_bucket(
                    self._graph_client,
                    bucket_id,
                    plan_id,
                    task_in_template_bucket["title"],
                    order_hint,
                )
                if new_task:
                    bucket_details["tasks_info"].append({"id": new_task.id, "title": new_task.title})
                template_tasks_index -= 1
            del tasks_in_bucket_4_plan
        self.populate_task_details_from_template(plan_id, bucket_details_4_plan, tasks_in_template_bucket)

    def populate_task_details_from_template(
        self, plan_id: str, bucket_details_4_plan: dict = None, tasks_in_template_bucket: list = None
    ):
        """Populates the task details in weekly meeting plan buckets from weekly meeting meeting template plan"""
        logger.info(f"Populating weekly meeting task details from template in plan {plan_id}")
        if tasks_in_template_bucket is None or bucket_details_4_plan is None:
            logger.info("The template tasks and/or target plan bucket details were not provided.")
            return
        logger.debug(f"Tasks in template bucket: {tasks_in_template_bucket}")
        logger.debug(f"Bucket details for plan: {bucket_details_4_plan}")
        for bucket_id, bucket_details in bucket_details_4_plan.items():
            logger.info(f"Updating tasks in bucket name {bucket_details['bucket_name']}")
            tasks_in_bucket_4_plan = bucket_details["tasks_info"]
            template_tasks_index = len(tasks_in_template_bucket) - 1
            # Preserve order of tasks by looping in reverse with the provided order hint
            while template_tasks_index >= 0:
                task_in_template_bucket = tasks_in_template_bucket[template_tasks_index]
                if tasks_in_bucket_4_plan:
                    for task_in_bucket_4_plan in tasks_in_bucket_4_plan:
                        if task_in_bucket_4_plan["title"] == task_in_template_bucket["title"]:
                            due_date_part: str = bucket_details["bucket_name"].split()[0]
                            if datetime.strptime(due_date_part, "%Y%m%d").date() < date.today():
                                logger.info(
                                    f"Skipping task update as due date {due_date_part} has passed for task with\
                                          name {task_in_bucket_4_plan['title']} in bucket id {bucket_id}"
                                )
                            logger.info(
                                f"Updating task for task with name {task_in_bucket_4_plan['title']}\
                                      in bucket id {bucket_id}"
                            )
                            self._update_planner_task(
                                task_id=task_in_bucket_4_plan["id"],
                                due_date_time=f"{due_date_part[0:4]}-"
                                f"{due_date_part[4:6]}-"
                                f"{due_date_part[6:8]}T12:00:00Z",
                            )
                            logger.info(
                                f"Updating task details for task with\
                                      name {task_in_bucket_4_plan['title']} in bucket id {bucket_id}"
                            )
                            task_details_in_template = PlannerHelper.fetch_task_details(
                                self._graph_client, task_in_template_bucket["id"]
                            )
                            logger.debug(task_in_bucket_4_plan)
                            self._update_planner_task_details(
                                task_in_bucket_4_plan["id"],
                                task_details_in_template.description,
                                task_details_in_template.references,
                            )
                            break
                template_tasks_index -= 1
            del tasks_in_bucket_4_plan

    # GET https://graph.microsoft.com/v1.0/planner/buckets/{bucket-id}/tasks
    def _fetch_tasks_in_bucket(self, bucket_id):
        """Fetches the tasks in a planner bucket with specified id"""
        try:
            logger.debug(f"Fetching the planner tasks from buucket {bucket_id}")
            graph_helper: GraphHelper = GraphHelper()
            tasks = graph_helper.get_request(
                f"planner/buckets/{bucket_id}/tasks",
                {"Content-Type": "application/json"},
            )
            if tasks and tasks["value"] is not None:
                logger.debug(f"Found {len(tasks['value'])} tasks in bucket {bucket_id}.")
                planner_tasks = []
                for task in tasks['value']:
                    planner_task = PlannerTask()
                    planner_task.id = task["id"]
                    planner_task.title = task["title"]
                    planner_task.percent_complete = task["percentComplete"]
                    planner_task.priority = task["priority"]
                    if task["dueDateTime"] is not None:
                        planner_task.due_date_time = datetime.strptime(task["dueDateTime"], "%Y-%m-%dT%H:%M:%SZ")
                    if task["assignments"] is not None:
                        planner_task.assignments = PlannerAssignments(additional_data = task["assignments"])
                    planner_tasks.append(planner_task)
                logger.debug(f"Tasks: {planner_tasks}")
                return planner_tasks
        except AgendaException as e:
            logger.error(f"Error getting tasks from bucket { {bucket_id}}. {e}")
        return None
    
    # PATCH https://graph.microsoft.com/v1.0/planner/tasks/{task-id}
    # Content-type: application/json
    # Prefer: return=representation
    # If-Match: W/"JzEtVGFzayAgQEBAQEBAQEBAQEBAQEBAWCc="

    # {
    #   "assignments": {
    #     "fbab97d0-4932-4511-b675-204639209557": {
    #       "@odata.type": "#microsoft.graph.plannerAssignment",
    #       "orderHint": "N9917 U2883!"
    #     }
    #   },
    #   "appliedCategories": {
    #     "category3": true,
    #     "category4": false
    #   }
    # }
    def _update_planner_task(
        self,
        task_id: str,
        due_date_time: str,
        assigned_user_id: str = None,
        percent_complete: int = 0,
        unassign_user: bool = False,
    ):
        """Update the planner task"""
        try:
            logger.debug(f"Updating the planner task {task_id}")
            task = PlannerHelper.fetch_task(self._graph_client, task_id)
            assignments = {}
            if assigned_user_id is not None:
                if unassign_user:
                    assignments = {assigned_user_id: None}
                else:
                    assignments = {
                        assigned_user_id: {"@odata.type": "#microsoft.graph.plannerAssignment", "orderHint": " !"}
                    }
            task_data = {
                "bucketId": task.bucket_id,
                "title": task.title,
                "assignments": assignments,
                "priority": task.priority,
                "dueDateTime": due_date_time,
                "percentComplete": percent_complete,
            }
            etag = task.additional_data["@odata.etag"]
            graph_helper: GraphHelper = GraphHelper()
            data_json = json.dumps(task_data)
            logger.debug(data_json)
            task_update_result = graph_helper.patch_request(
                f"planner/tasks/{task_id}",
                data_json,
                {"Content-Type": "application/json", "If-Match": etag},
            )
            if task_update_result:
                logger.debug(f"Task update result {task_update_result}")
                return task_update_result
        except AgendaException as e:
            logger.error(f"Error updating task {task_id}. {e}")
        return None

    # PATCH https://graph.microsoft.com/v1.0/planner/tasks/{task-id}/details
    # Content-type: application/json
    # Prefer: return=representation
    # If-Match: W/"JzEtVGFzayAgQEBAQEBAQEBAQEBAQEBAWCc="
    # {
    # "previewType": "noPreview",
    # "references": {
    #     "http%3A//developer%2Emicrosoft%2Ecom":{
    #     "@odata.type": "microsoft.graph.plannerExternalReference",
    #     "alias": "Documentation",
    #     "previewPriority": " !",
    #     "type": "Other"
    #     },
    #     "https%3A//developer%2Emicrosoft%2Ecom/en-us/graph/graph-explorer":{
    #     "@odata.type": "microsoft.graph.plannerExternalReference",
    #     "previewPriority": "  !!",
    #     },
    #     "http%3A//www%2Ebing%2Ecom": null
    # },
    # "checklist": {
    #     "95e27074-6c4a-447a-aa24-9d718a0b86fa":{
    #     "@odata.type": "microsoft.graph.plannerChecklistItem",
    #     "title": "Update task details",
    #     "isChecked": true
    #     },
    #     "d280ed1a-9f6b-4f9c-a962-fb4d00dc50ff":{
    #     "@odata.type": "microsoft.graph.plannerChecklistItem",
    #     "isChecked": true,
    #     },
    #     "a93c93c5-10a6-4167-9551-8bafa09967a7": null
    # }
    # }
    def _update_planner_task_details(self, task_id: str, description: str, references):
        """Update the planner task details"""
        try:
            logger.debug(f"Updating the planner task details for task {task_id}")
            task_details = PlannerHelper.fetch_task_details(self._graph_client, task_id)
            logger.debug(task_details)
            task_detail_references = {}
            order_hint = " !"
            if references.additional_data:
                for ref_url, ref_details in references.additional_data.items():
                    task_detail_references[ref_url] = {
                        "@odata.type": ref_details["@odata.type"],
                        "alias": ref_details["alias"],
                        "previewPriority": order_hint,
                        "type": ref_details["type"],
                    }
            task_details_2_update = {
                "additional_data": task_details.additional_data,
                "description": description,
                "references": task_detail_references,
            }
            etag = task_details.additional_data["@odata.etag"]
            graph_helper: GraphHelper = GraphHelper()
            logger.debug(f"task details dict: {task_details_2_update}")
            data_json = json.dumps(task_details_2_update)
            logger.debug(f"task details json: {data_json}")
            task_update_result = graph_helper.patch_request(
                f"planner/tasks/{task_id}/details",
                data_json,
                {"Content-Type": "application/json", "If-Match": etag},
            )
            logger.debug(task_update_result)
            if task_update_result:
                logger.debug(f"Task details update result {task_update_result}")
                return task_update_result
        except AgendaException as e:
            logger.error(f"Error updating task {task_id}. {e}")
        return None

    def get_assigned_to_user(self, task):
        """Gets assigned to user for task"""
        retry_count = 0
        assigned_to_user = None
        while retry_count < 5:
            try:
                logger.debug(f"Getting the assigned to user for task: {task.title}")
                assigned_to_users = list(task.assignments.additional_data.keys())
                if assigned_to_users is not None and len(assigned_to_users) > 0:
                    assigned_to_user_id = list(task.assignments.additional_data.keys())[0]
                    user = asyncio.run(UserHelper.get_user(self._graph_client, assigned_to_user_id))
                    if user is not None:
                        return user
                else:
                    return assigned_to_user
            except RuntimeError as e:
                if "Event loop is closed" in str(e):
                    if retry_count < 5:
                        retry_count = retry_count + 1
                        time.sleep(10)
                    else:
                        logger.error(f"Error getting assigned user. {e}")
                        break  # do something here, like log the error
        return assigned_to_user

    def sync_weekly_meeting_signup_with_plan(self, plan_name: str):
        """Sync the weekly meeting signup tasks plan with the specified name"""
        logger.info(f"Syncing the weekly meeting signup tasks with plan {plan_name}")

        plan = PlannerHelper.get_plan_by_exact_name(self._graph_client, self._group_id, plan_name)
        if plan is None:
            logger.error(f"Plan with name {plan_name} was not found.")
            return
        next_weeks_bucket = PlannerHelper.get_bucket_by_name(self._graph_client, plan.id, self._next_tuesday_date)
        if next_weeks_bucket is None:
            logger.error(f"Next weeks bucket '{self._next_tuesday_date}' was not found.")
            return
        tasks_in_next_weeks_bucket = self._fetch_tasks_in_bucket(next_weeks_bucket.id)
        if tasks_in_next_weeks_bucket is None:
            logger.info(f"There are no new tasks in the '{self._next_tuesday_date}' bucket.")
            return
        speaker_ids = []
        evaulator_ids = []
        for functionary_role_name, signup_task in self.get_functionary_signups(self._next_tuesday).items():
            if signup_task is None:
                continue
            for next_weeks_task in tasks_in_next_weeks_bucket:
                assigned_to_user = self.get_assigned_to_user(next_weeks_task)
                if assigned_to_user is not None:
                    if "Speaker" in next_weeks_task.title:
                        speaker_ids.append(assigned_to_user.id)
                    if "Manual Evaluator" in next_weeks_task.title:
                        evaulator_ids.append(assigned_to_user.id)
                    continue
                if functionary_role_name in next_weeks_task.title.strip().title():
                    signup_assigned_to_user = self.get_assigned_to_user(signup_task)
                    if "Speaker" in next_weeks_task.title and (
                        len(speaker_ids) == 3 or signup_assigned_to_user.id in speaker_ids
                    ):
                        continue
                    if "Manual Evaluator" in next_weeks_task.title and (
                        len(evaulator_ids) == 3 or signup_assigned_to_user.id in evaulator_ids
                    ):
                        continue
                    logger.debug(
                        f"Assigining '{signup_assigned_to_user.display_name}' as '{functionary_role_name}' for next week."
                    )
                    self._update_planner_task(
                        task_id=next_weeks_task.id,
                        due_date_time=f"{self._next_tuesday_date[0:4]}-"
                        f"{self._next_tuesday_date[4:6]}-"
                        f"{self._next_tuesday_date[6:8]}T12:00:00Z",
                        assigned_user_id=signup_assigned_to_user.id,
                    )
                    break

    def close_past_due_weekly_meeting_signup_tasks(self):
        """Close all the past due signup tasks"""
        logger.info(f"Closing all past due weekly meeting signup tasks")
        signup_plan = PlannerHelper.get_plan_by_exact_name(self._graph_client, self._group_id, "Weekly Meeting Signup")
        if signup_plan is None:
            logger.error("The Weekly Meeting Signup Plan was not found.")
            return
        signup_bucket = PlannerHelper.get_bucket_by_name(self._graph_client, signup_plan.id, "Functionary Role")
        if signup_bucket is None:
            logger.error("The Weekly Meeting Plan bucket 'Functionary Role' was not found.")
            return
        tmp_tasks_in_signup_bucket = self._fetch_tasks_in_bucket(signup_bucket.id)
        if tmp_tasks_in_signup_bucket is None:
            logger.info("There are no new task signups in the 'Functionary Role' bucket.")
            return
        for tmp_signup_task in tmp_tasks_in_signup_bucket:
            if tmp_signup_task.percent_complete < 100 and tmp_signup_task.due_date_time.date() < date.today():
                self._update_planner_task(
                    task_id=tmp_signup_task.id,
                    due_date_time=f'{tmp_signup_task.due_date_time.strftime("%Y-%m-%d")}T12:00:00Z',
                    assigned_user_id=self.get_assigned_to_user(tmp_signup_task).id,
                    percent_complete=100,
                )
                continue

    def unassign_absentee_tasks_in_plan(self, plan_name: str):
        """Unassign any tasks assigned to absentees in plan"""
        logger.info(f"Unassigning tasks assigned to absentees in plan {plan_name}")
        anbsentee_signups = self.get_absentee_signups(self._next_tuesday_date)
        if len(anbsentee_signups) == 0:
            return
        absentee_user_ids = []
        for absentee_task in self.get_absentee_signups(self._next_tuesday.date):
            absentee_user_ids.append(self.get_assigned_to_user(absentee_task).id)
        plan = PlannerHelper.get_plan_by_exact_name(self._graph_client, self._group_id, plan_name)
        if plan is None:
            logger.error(f"Plan with name {plan_name} was not found.")
            return
        next_weeks_bucket = PlannerHelper.get_bucket_by_name(self._graph_client, plan.id, self._next_tuesday_date)
        if next_weeks_bucket is None:
            logger.error(f"Next weeks bucket '{self._next_tuesday_date}' was not found.")
            return
        tasks_in_next_weeks_bucket = self._fetch_tasks_in_bucket(next_weeks_bucket.id)
        if tasks_in_next_weeks_bucket is None:
            logger.info(f"There are no new tasks in the '{self._next_tuesday_date}' bucket.")
            return
        for next_weeks_task in tasks_in_next_weeks_bucket:
            assigned_to_user = self.get_assigned_to_user(next_weeks_task)
            logger.debug(f"Assigned user: {assigned_to_user}, Absentee user ids: {absentee_user_ids}")
            if assigned_to_user is not None and assigned_to_user.id in absentee_user_ids:
                self._update_planner_task(
                    task_id=next_weeks_task.id,
                    due_date_time=f"{self._next_tuesday_date[0:4]}-"
                    f"{self._next_tuesday_date[4:6]}-"
                    f"{self._next_tuesday_date[6:8]}T12:00:00Z",
                    assigned_user_id=assigned_to_user.id,
                    unassign_user=True,
                )

    def get_functionary_signups(self, meeting_date: date = None, check_signup_assignments: bool = True) -> dict:
        """Get all functionaries signups for the meeting date"""
        functionary_signups: dict = {
            "Joke Master": None,
            "Toastmaster": None,
            "General Evaluator": None,
            "Speaker 1": None,
            "Speaker 2": None,
            "Speaker 3": None,
            "Manual Evaluator 1": None,
            "Manual Evaluator 2": None,
            "Manual Evaluator 3": None,
            "Ah Counter": None,
            "Grammarian": None,
            "Timer": None,
            "Ballot Counter": None,
            "WOW": None,
            "GEM": None,
        }
        if not check_signup_assignments:
            return functionary_signups
        signup_plan = PlannerHelper.get_plan_by_exact_name(self._graph_client, self._group_id, "Weekly Meeting Signup")
        if signup_plan is None:
            logger.error("The Weekly Meeting Signup Plan was not found.")
            return functionary_signups
        signup_bucket = PlannerHelper.get_bucket_by_name(self._graph_client, signup_plan.id, "Functionary Role")
        if signup_bucket is None:
            logger.error("The Weekly Meeting Plan bucket 'Functionary Role' was not found.")
            return functionary_signups
        tmp_tasks_in_signup_bucket = self._fetch_tasks_in_bucket(signup_bucket.id)
        if tmp_tasks_in_signup_bucket is None:
            logger.info("There are no new task signups in the 'Functionary Role' bucket.")
            return functionary_signups
        for tmp_signup_task in tmp_tasks_in_signup_bucket:
            if tmp_signup_task.percent_complete < 100 and tmp_signup_task.due_date_time.date() < date.today():
                continue
            if tmp_signup_task.title == "Absent":
                continue
            if tmp_signup_task.percent_complete < 100 and (
                tmp_signup_task.due_date_time.strftime("%Y%m%d") == meeting_date.strftime("%Y%m%d")
            ):
                logger.debug(
                    f"Found signup task {tmp_signup_task.title}, \
                        completion {tmp_signup_task.percent_complete}%, \
                            due {tmp_signup_task.due_date_time}"
                )
                speaker_count = 1
                manual_evaluator_count = 1
                if "Speaker" in tmp_signup_task.title:
                    while speaker_count <= 3 and functionary_signups[f"Speaker {speaker_count}"] != None:
                        speaker_count += 1
                        continue
                    if speaker_count == 3:
                        logger.debug(f"All 3 speaker roles have been filled.")
                        continue
                    functionary_signups[f"Speaker {speaker_count}"] = tmp_signup_task
                    continue
                if "Manual Evaluator" in tmp_signup_task.title:
                    while (
                        manual_evaluator_count <= 3
                        and functionary_signups[f"Manual Evaluator {manual_evaluator_count}"] != None
                    ):
                        manual_evaluator_count += 1
                        continue
                    if manual_evaluator_count == 3:
                        logger.debug(f"All 3 Manual Evaluator roles have been filled.")
                        continue
                    functionary_signups[f"Manual Evaluator  {manual_evaluator_count}"] = tmp_signup_task
                    continue
                if "GEM" in tmp_signup_task.title:
                    functionary_signups["GEM"] = tmp_signup_task
                    continue
                if "WOW" in tmp_signup_task.title:
                    functionary_signups["WOW"] = tmp_signup_task
                    continue
                functionary_signups[tmp_signup_task.title] = tmp_signup_task

        logger.debug(f"Functionary Signup: {functionary_signups}")
        return functionary_signups

    def get_absentee_signups(self, meeting_date: date):
        """Get all the absentee signups for the meeting date"""
        absentee_signups: list = []
        signup_plan = PlannerHelper.get_plan_by_exact_name(self._graph_client, self._group_id, "Weekly Meeting Signup")
        if signup_plan is None:
            logger.error("The Weekly Meeting Signup Plan was not found.")
            return absentee_signups
        signup_bucket = PlannerHelper.get_bucket_by_name(self._graph_client, signup_plan.id, "Functionary Role")
        if signup_bucket is None:
            logger.error("The Weekly Meeting Plan bucket 'Functionary Role' was not found.")
            return absentee_signups
        tmp_tasks_in_signup_bucket = self._fetch_tasks_in_bucket(signup_bucket.id)
        if tmp_tasks_in_signup_bucket is None:
            logger.info("There are no new task signups in the 'Functionary Role' bucket.")
            return absentee_signups
        for tmp_signup_task in tmp_tasks_in_signup_bucket:
            if tmp_signup_task.title == "Absent" and tmp_signup_task.due_date_time.date() == meeting_date:
                absentee_signups.append(tmp_signup_task)
                absentee_user = self.get_assigned_to_user(tmp_signup_task)
                logger.debug(
                    f"Found absentee task, \
                        assigned to {absentee_user.display_name}"
                )

        return absentee_signups
