import asyncio
import time
from msgraph import GraphServiceClient
from kiota_abstractions.api_error import APIError


class ExcelHelper:
    """This is a helper for MS Excel"""

    @staticmethod
    # GET /drives/{drive-id}/workbook/worksheets
    async def get_worksheets(
        graph_client: GraphServiceClient, drive_id: str, item_id: str
    ):
        """Gets all the worksheetsq"""
        try:
            print(f"Getting all worksheets for workbook in excel file {item_id}")
            worksheets = (
                await graph_client.drives.by_drive_id(drive_id)
                .items.by_drive_item_id(item_id)
                .workbook.worksheets.get()
            )
            return worksheets
        except APIError as e:
            print(f"Error: {e.error.message}")
        return None

    @staticmethod
    # GET /drives/{drive-id}/items/{id}/workbook/worksheets/{id|name}/range(address='A1:B2')?$select=values
    async def get_range(
        graph_client: GraphServiceClient,
        drive_id: str,
        item_id: str,
        worksheet_id: str,
        range_address: str,
    ):
        """Gets the range value of specified range address"""
        print(
            f"Gets the range value in excel file {item_id} for worksheet {worksheet_id} of specified range address {range_address}"
        )
        try:
            # range_address_query = "{" + range_address + "}"
            print(f"Getting range {range_address}")
            range_value = (
                await graph_client.drives.by_drive_id(drive_id)
                .items.by_drive_item_id(item_id)
                .workbook.worksheets.by_workbook_worksheet_id(worksheet_id)
                .range_with_address(range_address)
                .get()
            )
            print(range_value)
            return range_value
        except APIError as e:
            print(f"Error: {e.error.message}")
        return None

    @staticmethod
    # GET /drives/{drive-id}/items/{id}/workbook/worksheets/{id|name}/cell(row=<row>,column=<column>)
    async def get_cell(
        graph_client: GraphServiceClient,
        drive_id: str,
        item_id: str,
        worksheet_id: str,
        row: int,
        column: int,
    ):
        """Gets the range value of specified range address"""
        print(
            f"Gets the cell in excel file {item_id} for worksheet {worksheet_id} of specified cell row={row}, column={column}"
        )
        try:
            print(f"Getting cell {row}x{column}")
            cell = (
                await graph_client.drives.by_drive_id(drive_id)
                .items.by_drive_item_id(item_id)
                .workbook.worksheets.by_workbook_worksheet_id(worksheet_id)
                .cell_with_row_with_column(column, row)
                .get()
            )
            print(cell)
            return cell
        except APIError as e:
            print(f"Error: {e.error.message}")
        return None

    @staticmethod
    def get_cell_value(
        graph_client: GraphServiceClient,
        drive_id: str,
        item_id: str,
        worksheet_id: str,
        row: int,
        column: int,
    ):
        """Get the cell value from worksheet"""
        retry_count = 0
        cell_value = None
        while retry_count < 3:
            try:
                print(f"Getting the cell value: {row}x{column}")
                cell = asyncio.run(
                    ExcelHelper.get_cell(
                        graph_client, drive_id, item_id, worksheet_id, row, column
                    )
                )
                if cell and cell.values:
                    return cell.values
            except RuntimeError as e:
                if "Event loop is closed" in str(e):
                    if retry_count < 5:
                        retry_count = retry_count + 1
                        time.sleep(10)
                    else:
                        raise e
        return cell_value
