from urllib.parse import quote
from loguru import logger
from msgraph import GraphServiceClient
from msgraph.generated.models.folder import Folder
from msgraph.generated.models.drive_item import DriveItem
from msgraph.generated.drives.item.items.item.copy.copy_post_request_body import (
    CopyPostRequestBody,
)
from msgraph.generated.models.item_reference import ItemReference
from kiota_abstractions.api_error import APIError


class DriveHelper:
    """This is a helper for Onedrive"""

    @staticmethod
    # GET /groups/{group-id}/drive')
    async def get_drive(graph_client: GraphServiceClient, group_id: str):
        """Gets the drive for the group"""
        try:
            logger.debug(f"Getting the drive for group {group_id}")
            drive = await graph_client.groups.by_group_id(group_id).drive.get()
            return drive
        except APIError as e:
            logger.error(f"Error getting drive: {e.error.message}")
        return None

    @staticmethod
    # GET /groups/{group-id}/drive/special/{item-id}
    async def get_drive_special(graph_client: GraphServiceClient, drive_id: str, item_id: str):
        """Gets the drive special for the drive id"""
        try:
            logger.debug(f"Getting the drive special matching item id {item_id}")
            special_item = await graph_client.drives.by_drive_id(drive_id).special.by_drive_item_id(item_id).get()
            return special_item
        except APIError as e:
            logger.error(f"Error getting drive special: {e.error.message}")
        return None

    @staticmethod
    # GET /drives/{drive-id}/root:/{path-relative-to-root}:/children
    async def get_children_by_path(graph_client: GraphServiceClient, drive_id: str, relative_path: str = None):
        """Gets the children for the drive id matching url"""
        try:
            path_suffix = "root/children"
            if relative_path is not None:
                path_suffix = f"root:/{quote(relative_path)}/:children"
            url_by_path = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/{path_suffix}"
            logger.debug(f"Getting the children matching url {url_by_path}")
            children = await graph_client.drives.with_url(url_by_path).get()
            return children
        except APIError as e:
            logger.error(f"Error getting children by relative path: {e.error.message}")
        return None

    @staticmethod
    # GET /drives/{drive-id}/root:/{path-relative-to-root}
    async def get_item_by_path(graph_client: GraphServiceClient, drive_id: str, relative_path: str = None):
        """Gets the children for the drive id matching url"""
        try:
            path_suffix = "root/children"
            if relative_path is not None:
                path_suffix = f"root:/{quote(relative_path)}"
            url_by_path = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/{path_suffix}"
            logger.debug(f"Getting the item matching url {url_by_path}")
            item = await graph_client.drives.with_url(url_by_path).get()
            return item
        except APIError as e:
            logger.error(f"Error getting drive item by path: {e.error.message}")
        return None

    @staticmethod
    # GET /drives/{drive-id}/root/children
    async def get_children_of_root(graph_client: GraphServiceClient, drive_id: str):
        """Gets the children of root for the drive id"""
        try:
            logger.debug(f"Getting the children of root matching for drive id {drive_id}")
            children = await graph_client.drives.by_drive_id(drive_id).root.get()
            return children
        except APIError as e:
            logger.error(f"Error getting children of root: {e.error.message}")
        return None

    @staticmethod
    # GET /drives/{drive-id}/items/{item-id}/children
    async def get_children_by_item(graph_client: GraphServiceClient, drive_id: str, item_id: str):
        """Gets the children for the drive id matching sub path"""
        try:
            logger.debug(f"Getting the children matching item id {item_id}")
            children = await graph_client.drives.by_drive_id(drive_id).items.by_drive_item_id(item_id).children.get()
            return children
        except APIError as e:
            logger.error(f"Error getting children by item id {item_id}: {e.error.message}")
        return None

    @staticmethod
    # GET /drives/{drive-id}/items/{parent-item-id}/children
    async def create_folder(
        graph_client: GraphServiceClient,
        drive_id: str,
        parent_item_id: str,
        folder_name: str,
    ):
        """Create a folder under the parent item"""
        try:
            logger.debug(f"Creating a folder {folder_name} under item id {parent_item_id}")
            request_body = DriveItem(
                name=folder_name,
                folder=Folder(),
                additional_data={
                    "@microsoft_graph_conflict_behavior": "fail",
                },
            )
            folder_result = (
                await graph_client.drives.by_drive_id(drive_id)
                .items.by_drive_item_id(parent_item_id)
                .children.post(request_body)
            )
            return folder_result
        except APIError as e:
            logger.error(f"Error creating folder {folder_name}: {e.error.message}")
        return None

    @staticmethod
    # GET /drives/{drive-id}/items/{parent-item-id}/children
    async def copy_item(
        graph_client: GraphServiceClient,
        drive_id: str,
        source_item_id: str,
        dest_parent_item_id: str,
        dest_item_name: str,
    ):
        """Create a folder under the parent item"""
        try:
            logger.debug(
                f"Copying item {dest_item_name} with id {source_item_id}\
                      to destination with parent id {dest_parent_item_id}"
            )
            request_body = CopyPostRequestBody(
                parent_reference=ItemReference(
                    drive_id=drive_id,
                    id=dest_parent_item_id,
                ),
                name=dest_item_name,
            )
            copy_result = (
                await graph_client.drives.by_drive_id(drive_id)
                .items.by_drive_item_id(source_item_id)
                .copy.post(request_body)
            )
            return copy_result
        except APIError as e:
            logger.error(f"Error copying item to {dest_item_name}: {e.error.message}")
        return None
