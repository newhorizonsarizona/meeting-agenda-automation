import asyncio
from loguru import logger
import time
from msgraph import GraphServiceClient
from msgraph.generated.planner.plans.item.planner_plan_item_request_builder import (
    PlannerPlanItemRequestBuilder,
)
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
                        time.sleep(10)
                    else:
                        logger.error(f"Unexpected error getting plan {plan_name}. {e}")
                        break  # do something here, like log the error
        return plan_by_name

    @staticmethod
    def get_bucket_by_name(graph_client, plan_id, bucket_name):
        """Gets bucket by name for the specified plan id"""
        retry_count = 0
        bucket_by_name = None
        while retry_count < 5:
            try:
                logger.debug(f"Getting the bucket in plan: {plan_id}")
                buckets = asyncio.run(PlannerHelper.get_all_buckets(graph_client, plan_id))
                if buckets and buckets.value:
                    for bucket in buckets.value:
                        if bucket_name in bucket.name:
                            logger.debug(f"Found bucket {bucket}")
                            return bucket
            except RuntimeError as e:
                if "Event loop is closed" in str(e):
                    if retry_count < 5:
                        retry_count = retry_count + 1
                        time.sleep(10)
                    else:
                        logger.error(f"Unexpected error getting bucket {bucket_name}. {e}")
                        break  # do something here, like log the error
        return bucket_by_name

    @staticmethod
    def fetch_tasks_in_bucket(graph_client, bucket_id):
        """Fetches all the tasks in the bucket"""
        retry_count = 0
        tasks_in_bucket = None
        while retry_count < 5:
            try:
                logger.debug(f"Getting the tasks in bucket: {bucket_id}")
                tasks = asyncio.run(PlannerHelper.get_tasks_in_bucket(graph_client, bucket_id))
                if tasks and tasks.value:
                    return tasks
            except RuntimeError as e:
                if "Event loop is closed" in str(e):
                    if retry_count < 5:
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
        plan_by_name = None
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
