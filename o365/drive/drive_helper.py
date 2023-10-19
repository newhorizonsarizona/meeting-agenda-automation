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
    # GET /groups/{group-id}/drive/items/{item-id}
    async def get_drive_item(graph_client: GraphServiceClient, drive_id: str, item_id: str):
        """Gets the drive item for the drive id"""
        try:
            print(f'Getting the drive item matching item id {item_id}')
            drive_item = await graph_client.drives.by_drive_id(drive_id).items.by_drive_item_id(item_id).get()
            return drive_item
        except APIError as e:
            print(f'Error: {e.error.message}')
