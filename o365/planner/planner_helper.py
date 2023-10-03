import json
import httpx
from logging import Logger

class PlannerHelper:
    """This is a helper for MS Planner"""

    @staticmethod
    def get_all_tasks(group_id: str, access_token: str):
        """Gets all the planner tasks"""
        print('Getting all tasks')
        # Define the Microsoft Graph API endpoint for Planner tasks
        graph_url = f'https://graph.microsoft.com/v1.0/{group_id}/planner/tasks'

        # Make a GET request to retrieve tasks
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

        async def get_planner_tasks():
            async with httpx.AsyncClient() as client:
                response = await client.get(graph_url, headers=headers)
                if response.status_code == 200:
                    tasks = response.json()
                    # Process and print the tasks as needed
                    print(json.dumps(tasks, indent=4))
                else:
                    print(f"Error: {response.status_code} - {response.text}")

        import asyncio
        asyncio.run(get_planner_tasks())
