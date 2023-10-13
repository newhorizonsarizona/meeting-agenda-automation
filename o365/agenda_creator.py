import asyncio
from logging import Logger
from auth.auth_helper import AuthHelper
from planner.planner_helper import PlannerHelper
    
group_id = 'aa235df6-19fc-4de3-8498-202b5cbe2d15'

class AgendaCreator:
    """This class is used for creating the agenda"""

    def next_meeting_tasks(self):
        """Get the planner tasks for next meeting"""
        print('Creating agenda')
        plans = asyncio.run(PlannerHelper.get_all_plans(group_id))
        print(plans)
        if plans and plans.value:
            for plan in plans.value:
                buckets = asyncio.run(PlannerHelper.get_all_buckets(plan.id))
                print(buckets)

agenda_creator: AgendaCreator = AgendaCreator()
agenda_creator.next_meeting_tasks()