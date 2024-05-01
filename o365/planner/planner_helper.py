import asyncio
from datetime import date
import time
from loguru import logger
from msgraph import GraphServiceClient
from msgraph.generated.planner.plans.item.planner_plan_item_request_builder import (
    PlannerPlanItemRequestBuilder,
)
from msgraph.generated.planner.buckets.item.planner_bucket_item_request_builder import PlannerBucketItemRequestBuilder

from msgraph.generated.models.planner_plan import PlannerPlan
from msgraph.generated.models.planner_plan_container import PlannerPlanContainer
from msgraph.generated.models.planner_bucket import PlannerBucket
from msgraph.generated.models.planner_task import PlannerTask
from msgraph.generated.models.planner_assignments import PlannerAssignments
from kiota_abstractions.api_error import APIError


class PlannerHelper:
    """This is a helper for MS Planner"""

    @staticmethod
    # GET /groups/{group-id}/planner/plans
    async def get_all_plans(graph_client: GraphServiceClient, group_id: str):
        """Gets all the planner tasks"""
        try:
            logger.debug("Getting all plans")
            plans = await graph_client.groups.by_group_id(group_id).planner.plans.get()
            return plans
        except APIError as e:
            logger.error(f"Error getting all plans: {e.error.message}")

        return None

    @staticmethod
    # GET /planner/plans/{plan-id}/buckets
    async def get_all_buckets(graph_client: GraphServiceClient, plan_id: str):
        """Gets all the buckets in the plan"""
        logger.debug("Getting all buckets in the plan")
        try:
            buckets = await graph_client.planner.plans.by_planner_plan_id(plan_id).buckets.get()
            return buckets
        except APIError as e:
            logger.error(f"Error getting all buckets: {e.error.message}")
        return None

    @staticmethod
    # GET planner/buckets/{bucket-id}/tasks
    async def get_tasks_in_bucket(graph_client: GraphServiceClient, bucket_id: str):
        """Gets all the planner tasks in the bucket"""
        logger.debug("Getting all tasks in the bucket")
        try:
            tasks = await graph_client.planner.buckets.by_planner_bucket_id(bucket_id).tasks.get()
            return tasks
        except APIError as e:
            logger.error(f"Error getting all tasks in bucket: {e.error.message}")
        return None

    @staticmethod
    # GET /planner/plans/{plan-id}
    async def delete_plan(graph_client: GraphServiceClient, plan_id: str, etag: str = None):
        """Delete the plan with the specified id"""
        logger.debug(f"Deleting the plan with id {plan_id}")
        try:
            request_configuration = (
                PlannerPlanItemRequestBuilder.PlannerPlanItemRequestBuilderDeleteRequestConfiguration()
            )
            if etag is not None:
                request_configuration.headers.add("If-Match", etag)

            await graph_client.planner.plans.by_planner_plan_id(plan_id).delete(
                request_configuration=request_configuration
            )

        except APIError as e:
            logger.error(f"Error deleting plan: {e.error.message}")
        return None

    @staticmethod
    # GET /planner/plans
    async def create_plan(graph_client: GraphServiceClient, plan_name: str, group_id: str):
        """Creates the plan with the specified name in the group id"""
        logger.debug(f"Creating the plan with name {plan_name} in group {group_id}")
        try:
            request_body = PlannerPlan(
                container=PlannerPlanContainer(
                    url=f"https://graph.microsoft.com/v1.0/groups/{group_id}",
                ),
                title=plan_name,
            )
            result = await graph_client.planner.plans.post(request_body)
            return result
        except APIError as e:
            logger.error(f"Error creating plan: {e.error.message}")
        return None

    @staticmethod
    # GET /planner/buckets
    async def create_bucket(graph_client: GraphServiceClient, bucket_name: str, plan_id: str, order_hint: str = " !"):
        """Creates the bucket with the specified name in the plan id"""
        logger.debug(f"Creating the bucket with name {bucket_name} in plan {plan_id}")
        try:
            request_body = PlannerBucket(
                name=bucket_name,
                plan_id=plan_id,
                order_hint=order_hint,
            )

            result = await graph_client.planner.buckets.post(request_body)
            return result
        except APIError as e:
            logger.error(f"Error creating bucket: {e.error.message}")
        return None

    @staticmethod
    # GET /planner/buckets/{id}
    async def delete_bucket(graph_client: GraphServiceClient, plan_id: str, bucket_id: str):
        """Delete the bucket with the specified id"""
        logger.debug(f"Deleting the plan with id {plan_id}")
        try:
            request_configuration = (
                PlannerBucketItemRequestBuilder.PlannerBucketItemRequestBuilderDeleteRequestConfiguration()
            )
            request_configuration.headers.add("If-Match", plan_id)

            await graph_client.planner.buckets.by_planner_bucket_id(bucket_id).delete(
                request_configuration=request_configuration
            )

        except APIError as e:
            logger.error(f"Error deleting bucket: {e.error.message}")
        return None

    @staticmethod
    # GET /planner/tasks
    async def create_task(graph_client: GraphServiceClient, task: PlannerTask):
        """Creates the task with the specified name. due date and assignment in the bucket id"""
        logger.debug(
            f"Creating the task with name {task.title}, due {task.due_date_time}, in bucket {task.bucket_id} for plan {task.plan_id}"
        )
        try:
            result = await graph_client.planner.tasks.post(task)

            return result
        except APIError as e:
            logger.error(f"Error creating task: {e.error.message}")
        return None

    @staticmethod
    def get_plan_by_name(graph_client: GraphServiceClient, group_id: str, plan_name: str):
        """Gets plan by name for the specified group_id"""
        retry_count = 0
        plan_by_name = None
        while retry_count < 3:
            try:
                logger.debug(f"Getting the plan in group: {group_id} with name {plan_name}")
                plans = asyncio.run(PlannerHelper.get_all_plans(graph_client, group_id))
                if plans and plans.value:
                    for plan in plans.value:
                        if plan_name.lower() in plan.title.lower():
                            logger.debug(f"Found plan {plan}")
                            return plan
            except RuntimeError as e:
                if "Event loop is closed" in str(e):
                    if retry_count < 3:
                        retry_count = retry_count + 1
                        time.sleep(5)
                    else:
                        logger.error(f"Unexpected error getting plan {plan_name}. {e}")
                        break  # do something here, like log the error
        return plan_by_name

    @staticmethod
    def get_bucket_by_name(graph_client, plan_id, bucket_name):
        """Gets bucket by name for the specified plan id"""
        retry_count = 0
        bucket_by_name = None
        while retry_count < 3:
            try:
                logger.debug(f"Getting the bucket {bucket_name} in plan: {plan_id}")
                buckets = asyncio.run(PlannerHelper.get_all_buckets(graph_client, plan_id))
                if buckets and buckets.value:
                    for bucket in buckets.value:
                        if bucket_name in bucket.name:
                            logger.debug(f"Found bucket {bucket}")
                            return bucket
            except RuntimeError as e:
                if "Event loop is closed" in str(e):
                    if retry_count < 3:
                        retry_count = retry_count + 1
                        time.sleep(5)
                    else:
                        logger.error(f"Unexpected error getting bucket {bucket_name}. {e}")
                        break  # do something here, like log the error
        return bucket_by_name

    @staticmethod
    def fetch_all_buckets(graph_client, plan_id):
        """Fetches all the buckets for the specified plan id"""
        retry_count = 0
        buckets = None
        while retry_count < 3:
            try:
                logger.debug(f"Getting the buckets in plan: {plan_id}")
                buckets = asyncio.run(PlannerHelper.get_all_buckets(graph_client, plan_id))
                if buckets and buckets.value:
                    return buckets.value
            except RuntimeError as e:
                if "Event loop is closed" in str(e):
                    if retry_count < 3:
                        retry_count = retry_count + 1
                        time.sleep(5)
                    else:
                        logger.error(f"Unexpected error getting buckets. {e}")
                        break  # do something here, like log the error
        return buckets

    @staticmethod
    def get_task_by_name(graph_client, bucket_id, task_name):
        """Get the task with the specified name in the bucket"""
        retry_count = 0
        task_in_bucket = None
        while retry_count < 3:
            try:
                logger.debug(f"Getting the task {task_name} in bucket: {bucket_id}")
                tasks = asyncio.run(PlannerHelper.get_tasks_in_bucket(graph_client, bucket_id))
                if tasks and tasks.value:
                    for task in tasks.value:
                        if task.title == task_name:
                            return task
            except RuntimeError as e:
                if "Event loop is closed" in str(e):
                    if retry_count < 3:
                        retry_count = retry_count + 1
                        time.sleep(10)
                    else:
                        logger.error(f"Unexpected error getting task by name from bucket. {e}")
                        break  # do something here, like log the error
        return task_in_bucket

    @staticmethod
    def fetch_tasks_in_bucket(graph_client, bucket_id):
        """Fetches all the tasks in the bucket"""
        retry_count = 0
        tasks_in_bucket = None
        while retry_count < 3:
            try:
                logger.debug(f"Getting the tasks in bucket: {bucket_id}")
                tasks = asyncio.run(PlannerHelper.get_tasks_in_bucket(graph_client, bucket_id))
                if tasks and tasks.value:
                    return tasks.value
            except RuntimeError as e:
                if "Event loop is closed" in str(e):
                    if retry_count < 3:
                        retry_count = retry_count + 1
                        time.sleep(10)
                    else:
                        logger.error(f"Unexpected error getting tasks from bucket. {e}")
                        break  # do something here, like log the error
        return tasks_in_bucket

    @staticmethod
    def delete_plan_by_name(
        graph_client: GraphServiceClient,
        group_id: str,
        plan_name: str,
        etag: str = None,
    ):
        """Deletes plan by name for the specified group_id"""
        retry_count = 0
        while retry_count < 3:
            try:
                logger.debug(f"Getting the plan to delete with name {plan_name}")
                plan = PlannerHelper.get_plan_by_name(graph_client, group_id, plan_name)
                if plan is None:
                    logger.debug(f"No matching plan found with name {plan_name} in group {group_id}")
                    continue
                asyncio.run(PlannerHelper.delete_plan(graph_client, plan.id, etag))
            except RuntimeError as e:
                if "Event loop is closed" in str(e):
                    if retry_count < 3:
                        retry_count = retry_count + 1
                        time.sleep(10)
                    else:
                        logger.error(f"Unexpected error deleting plan {plan_name}. {e}")
                        break  # do something here, like log the error
        return True

    @staticmethod
    def create_plan_with_name(graph_client: GraphServiceClient, group_id: str, plan_name: str):
        """Creates a plan with specified name in the specified group_id"""
        retry_count = 0
        while retry_count < 3:
            try:
                logger.debug(f"Creating the plan with name {plan_name}")
                plan = asyncio.run(PlannerHelper.create_plan(graph_client, plan_name, group_id))
                return plan
            except RuntimeError as e:
                if "Event loop is closed" in str(e):
                    if retry_count < 3:
                        retry_count = retry_count + 1
                        time.sleep(10)
                    else:
                        logger.error(f"Unexpected error creating plan {plan_name}. {e}")
                        break  # do something here, like log the error
        return None

    @staticmethod
    def create_bucket_with_name(graph_client: GraphServiceClient, plan_id: str, bucket_name: str, order_hint: str):
        """Creates a bucket with with specified name in the specified plan_id"""
        retry_count = 0
        while retry_count < 3:
            try:
                logger.debug(f"Creating the bucket with name {bucket_name}")
                bucket = asyncio.run(PlannerHelper.create_bucket(graph_client, bucket_name, plan_id, order_hint))
                return bucket
            except RuntimeError as e:
                if "Event loop is closed" in str(e):
                    if retry_count < 3:
                        retry_count = retry_count + 1
                        time.sleep(10)
                    else:
                        logger.error(f"Unexpected error creating bucket {bucket_name}. {e}")
                        break  # do something here, like log the error
        return None

    @staticmethod
    def create_task_in_bucket(
        graph_client: GraphServiceClient,
        bucket_id: str,
        plan_id: str,
        task_title: str,
        order_hint: str = " !",
    ):
        """Creates a task with with specified name, due date, assignment in the specified bucket_id for plan_id"""
        retry_count = 0
        while retry_count < 1:
            try:
                logger.debug(f"Creating the task with name {task_title}, in bucket {bucket_id}")
                request_body = PlannerTask(
                    plan_id=plan_id,
                    bucket_id=bucket_id,
                    title=task_title,
                    assignments=None,
                    order_hint=order_hint,
                )
                task = asyncio.run(PlannerHelper.create_task(graph_client, request_body))
                return task
            except RuntimeError as e:
                if "Event loop is closed" in str(e):
                    if retry_count < 1:
                        retry_count = retry_count + 1
                        time.sleep(15)
                    else:
                        logger.error(f"Unexpected error creating task {task.title}. {e}")
                        break  # do something here, like log the error
        return None

    @staticmethod
    def delete_bucket_by_name(graph_client: GraphServiceClient, plan_id: str, bucket_name: str):
        """Deletes bucket by name for the specified bucket_id"""
        retry_count = 0
        while retry_count < 3:
            try:
                logger.debug(f"Getting the bucket to delete with name {bucket_name}")
                bucket = PlannerHelper.get_bucket_by_name(graph_client, plan_id, bucket_name)
                if bucket is None:
                    logger.debug(f"No matching bucket found with name {bucket_name} in group {plan_id}")
                    continue
                asyncio.run(PlannerHelper.delete_bucket(graph_client, plan_id, bucket.id))
            except RuntimeError as e:
                if "Event loop is closed" in str(e):
                    if retry_count < 3:
                        retry_count = retry_count + 1
                        time.sleep(10)
                    else:
                        logger.error(f"Unexpected error deleting bucke {bucket_name}. {e}")
                        break  # do something here, like log the error
        return True
