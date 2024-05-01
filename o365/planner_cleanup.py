from o365.auth.auth_helper import AuthHelper
from o365.planner.planner_helper import PlannerHelper


class PlannerCleanup:
    """This class is used for planner cleanup tasks"""

    def cleanup(self, plan_names: list, etag: str = None):
        """Cleanup the specified plans"""
        group_ids = ["bf608ce8-33de-40a0-a30d-97c596037f23"]
        graph_client = AuthHelper.graph_service_client_with_adapter()
        for group_id in group_ids:
            for plan_name in plan_names:
                print(f"Deleting plan with name {plan_name}")
                PlannerHelper.delete_plan_by_name(graph_client, group_id, plan_name, etag)
