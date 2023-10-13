from azure.identity.aio import ClientSecretCredential
from msgraph import GraphServiceClient
from kiota_abstractions.api_error import APIError

from auth.auth_helper import AuthHelper

class PlannerHelper:
    """This is a helper for MS Planner"""

    @staticmethod
    # GET /groups/{group-id}/planner/plans
    async def get_all_plans(group_id: str):
        """Gets all the planner tasks"""
        try:
            print('Getting all plans')
            credential : ClientSecretCredential = AuthHelper.client_service_credential()
            scopes = ['https://graph.microsoft.com/.default']
            graph_client = GraphServiceClient(credentials=credential, scopes=scopes)
            plans = await graph_client.groups.by_group_id(group_id).planner.plans.get()
            return plans
        except APIError as e:
            print(f'Error: {e.error.message}')


    @staticmethod
    # GET /planner/plans/{plan-id}/tasks
    async def get_all_tasks(plan_id: str):
        """Gets all the planner tasks"""
        print('Getting all tasks')
        credential : ClientSecretCredential = AuthHelper.client_service_credential()
        scopes = ['https://graph.microsoft.com/.default']
        graph_client = GraphServiceClient(credentials=credential, scopes=scopes)
        try:
            tasks = await graph_client.planner.plans.by_plan_id(plan_id).tasks.get()
            print(tasks)
        except APIError as e:
            print(f'Error: {e.error.message}')


    @staticmethod
    # GET /planner/plans/{plan-id}/buckets
    async def get_all_buckets(plan_id: str):
        """Gets all the buckets in the plan"""
        print('Getting all buckets in the plan')
        credential : ClientSecretCredential = AuthHelper.client_service_credential()
        scopes = ['https://graph.microsoft.com/.default']
        graph_client = GraphServiceClient(credentials=credential, scopes=scopes)
        try:
            tasks = await graph_client.planner.plans.by_plan_id(plan_id).buckets.get()
            print(tasks)
        except APIError as e:
            print(f'Error: {e.error.message}')

    @staticmethod
    # GET planner/buckets/{bucket-id}/tasks
    async def get_tasks_in_bucket(bucket_id: str):
        """Gets all the planner tasks in the bucket"""
        print('Getting all tasks in the bucket')
        credential : ClientSecretCredential = AuthHelper.client_service_credential()
        scopes = ['https://graph.microsoft.com/.default']
        graph_client = GraphServiceClient(credentials=credential, scopes=scopes)
        try:
            tasks = await graph_client.planner.buckets.by_bucket_id(bucket_id).tasks.get()
            print(tasks)
        except APIError as e:
            print(f'Error: {e.error.message}')