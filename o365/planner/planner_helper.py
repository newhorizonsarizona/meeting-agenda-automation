from msgraph import GraphServiceClient
from kiota_abstractions.api_error import APIError

class PlannerHelper:
    """This is a helper for MS Planner"""

    @staticmethod
    # GET /groups/{group-id}/planner/plans
    async def get_all_plans(graph_client: GraphServiceClient, group_id: str):
        """Gets all the planner tasks"""
        try:
            print('Getting all plans')
            plans = await graph_client.groups.by_group_id(group_id).planner.plans.get()
            return plans
        except APIError as e:
            print(f'Error: {e.error.message}')


    @staticmethod
    # GET /planner/plans/{plan-id}/buckets
    async def get_all_buckets(graph_client: GraphServiceClient, plan_id: str):
        """Gets all the buckets in the plan"""
        print('Getting all buckets in the plan')
        try:
            buckets = await graph_client.planner.plans.by_planner_plan_id(plan_id).buckets.get()
            return buckets
        except APIError as e:
            print(f'Error: {e.error.message}')

    @staticmethod
    # GET planner/buckets/{bucket-id}/tasks
    async def get_tasks_in_bucket(graph_client: GraphServiceClient, bucket_id: str):
        """Gets all the planner tasks in the bucket"""
        print('Getting all tasks in the bucket')
        try:
            tasks = await graph_client.planner.buckets.by_planner_bucket_id(bucket_id).tasks.get()
            return tasks
        except APIError as e:
            print(f'Error: {e.error.message}')