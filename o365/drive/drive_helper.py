from msgraph import GraphServiceClient
from kiota_abstractions.api_error import APIError

class DriveHelper:
    """This is a helper for Onedrive"""

    @staticmethod
    # GET /groups/{group-id}/drive')
    async def get_drive(graph_client: GraphServiceClient, group_id: str):
        """Gets the drive for the group"""
        try:
            print(f'Getting the drive for group {group_id}')
            drive = await graph_client.groups.by_group_id(group_id).drive.get()
            return drive
        except APIError as e:
            print(f'Error: {e.error.message}')

    @staticmethod
    # GET /drives/{drive-id}/root/search(q='{search-text}')
    async def get_drive_items(graph_client: GraphServiceClient, drive_id: str, query: str):
        """Gets the drive for the group"""
        try:
            print(f'Getting the drive items matching query {query}')
            drive_items = await graph_client.drives.by_drive_id(drive_id).root.get().search(q=query).get()
            return drive_items
        except APIError as e:
            print(f'Error: {e.error.message}')
