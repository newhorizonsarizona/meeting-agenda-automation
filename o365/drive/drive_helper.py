from msgraph import GraphServiceClient
from msgraph.generated.models.folder import Folder
from kiota_abstractions.api_error import APIError
from urllib.parse import quote

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
    # GET /groups/{group-id}/drive/special/{item-id}
    async def get_drive_special(graph_client: GraphServiceClient, drive_id: str, item_id: str):
        """Gets the drive special for the drive id"""
        try:
            print(f'Getting the drive special matching item id {item_id}')
            special_item = await graph_client.drives.by_drive_id(drive_id).special.by_drive_item_id(item_id).get()
            return special_item
        except APIError as e:
            print(f'Error: {e.error.message}')

    @staticmethod
    # GET /drives/{drive-id}/root:/{path-relative-to-root}:/children
    async def get_children_by_path(graph_client: GraphServiceClient, drive_id: str, relative_path: str=None):
        """Gets the children for the drive id matching url"""
        try:
            path_suffix = 'root/children'
            if relative_path is not None:
                path_suffix = f'root:/{quote(relative_path)}/:children'
            url_by_path = f'https://graph.microsoft.com/v1.0/drives/{drive_id}/{path_suffix}'
            print(f'Getting the children matching url {url_by_path}')
            children = await graph_client.drives.with_url(url_by_path).get()
            return children
        except APIError as e:
            print(f'Error: {e.error.message}')
        return None

    @staticmethod
    # GET /drives/{drive-id}/root/children
    async def get_children_of_root(graph_client: GraphServiceClient, drive_id: str):
        """Gets the children of root for the drive id"""
        try:
            print(f'Getting the children of root matching for drive id {drive_id}')
            children = await graph_client.drives.by_drive_id(drive_id).root.get()
            return children
        except APIError as e:
            print(f'Error: {e.error.message}')

    @staticmethod
    # GET /drives/{drive-id}/items/{item-id}/children
    async def get_children_by_item(graph_client: GraphServiceClient, drive_id: str, item_id: str):
        """Gets the children for the drive id matching sub path"""
        try:
            print(f'Getting the children matching item id {item_id}')
            children = await graph_client.drives.by_drive_id(drive_id).items.by_drive_item_id(item_id).children.get()
            return children
        except APIError as e:
            print(f'Error: {e.error.message}')

    @staticmethod
    # GET /drives/{drive-id}/items/{parent-item-id}/children
    async def create_folder(graph_client: GraphServiceClient, drive_id: str, parent_item_id: str, folder_name: str):
        """Create a folder under the parent item"""
        try:
            print(f'Creating a folder {folder_name} under item id {parent_item_id}')
            request_body = DriveItem(
                name = folder_name,
                folder = Folder(
                ),
                additional_data = {
                        "@microsoft_graph_conflict_behavior" : "rename",
                }
            )
            folder_result = await graph_client.drives.by_drive_id(drive_id).items.by_drive_item_id(parent_item_id).children.post(request_body)
            return folder_result
        except APIError as e:
            print(f'Error: {e.error.message}')
