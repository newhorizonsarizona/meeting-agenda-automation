import asyncio
import time
from msgraph import GraphServiceClient
from kiota_abstractions.api_error import APIError
from msgraph.generated.users.users_request_builder import UsersRequestBuilder

from o365.auth.auth_helper import AuthHelper


class UserHelper:
    """This is a helper for Office 365 users"""

    @staticmethod
    # GET /users/{id | userPrincipalName}
    async def get_user(graph_client: GraphServiceClient, user_id: str):
        """Gets the user"""
        try:
            print(f"Getting the user for id {user_id}")
            user = await graph_client.users.by_user_id(user_id).get()
            return user
        except APIError as e:
            print(f"Error: {e.error.message}")

    @staticmethod
    # GET /users?$filter=startswith(displayName,'a')&$orderby=displayName&$count=true&$top=1
    async def get_user_by_display_name(graph_client: GraphServiceClient, display_name: str):
        """Gets the user by display name"""
        try:
            query_params = UsersRequestBuilder.UsersRequestBuilderGetQueryParameters(
                select=["display_name", "id"],
                filter=f"startswith(display_name, '{display_name}')",
                orderby="display_name",
                count=False,
                top=1,
            )

            request_configuration = (
                UsersRequestBuilder.UsersRequestBuilderGetRequestConfiguration(
                    query_parameters=query_params,
                )
            )

            user = await graph_client.users.get(
                request_configuration=request_configuration
            )
            return user
        except APIError as e:
            print(f"Error: {e.error.message}")

    @staticmethod
    def get_assigned_to_user_by_display_name(graph_client, display_name):
        """Gets assigned to user by display name"""
        retry_count = 0
        assigned_to_user = None
        while retry_count < 5:
            try:
                print(f"Getting the assigned to user with display name : {display_name}")
                user = asyncio.run(
                    UserHelper.get_user_by_display_name(graph_client, display_name)
                )
                if user is not None:
                    print(user)
                    return user
                
            except RuntimeError as e:
                if "Event loop is closed" in str(e):
                    if retry_count < 5:
                        retry_count = retry_count + 1
                        time.sleep(10)
                    else:
                        print(e)
                        break  # do something here, like log the error
            except Exception as ex:
                print(ex)
                break  # do something here, like log the error

        return assigned_to_user
