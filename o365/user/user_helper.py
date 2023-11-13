from msgraph import GraphServiceClient
from kiota_abstractions.api_error import APIError

from auth.auth_helper import AuthHelper

class UserHelper:
    """This is a helper for Office 365 users"""

    @staticmethod
    # GET /users/{id | userPrincipalName}
    async def get_user(graph_client: GraphServiceClient, user_id: str):
        """Gets the user"""
        try:
            print(f'Getting the user for id {user_id}')
            user = await graph_client.users.by_user_id(user_id).get()
            return user
        except APIError as e:
            print(f'Error: {e.error.message}')