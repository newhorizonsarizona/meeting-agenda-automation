from logging import Logger
from auth.auth_helper import AuthHelper
from planner.planner_helper import PlannerHelper
    
group_id = 'aa235df6-19fc-4de3-8498-202b5cbe2d15'

class AgendaCreator:
    """This class is used for creating the agenda"""

    def next_meeting_tasks(self):
        """Get the planner tasks for next meeting"""
        print('Creating agenda')
        # Acquire a token
        result = AuthHelper.acquire_token()

        if 'access_token' in result:
            access_token = result['access_token']
            PlannerHelper.get_all_tasks(group_id, access_token)
        else:
            print(f"Authentication failed: {result.get('error_description')}")

agenda_creator: AgendaCreator = AgendaCreator()
agenda_creator.next_meeting_tasks()