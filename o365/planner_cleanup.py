from loguru import logger
from o365.auth.auth_helper import AuthHelper
from o365.exception.agenda_exception import AgendaException
from o365.graph.graph_helper import GraphHelper
from o365.planner.planner_helper import PlannerHelper
from o365.util.constants import Constants


class PlannerCleanup:
    """This class is used for planner cleanup tasks"""

    _graph_client = None
    _group_id: str

    def __init__(self):
        self._graph_client = AuthHelper.graph_service_client_with_adapter()
        self._group_id = Constants.GROUP_IDS[0]

    def cleanup(self, plan_names: list):
        """Cleanup the specified plans"""
        for plan_name in plan_names:
            logger.info(f"Deleting plan with name {plan_name}")
            plan = PlannerHelper.get_plan_by_exact_name(self._graph_client, self._group_id, plan_name)
            if plan is None:
                logger.info(f"The plan with {plan_name} was not found")
                return
            self._delete_plan(plan.id, plan.additional_data["@odata.etag"])

    # DELETE https://graph.microsoft.com/v1.0/planner/plans/{id}
    def _delete_plan(self, plan_id: str, etag: str):
        """Deleting plan with specified id"""
        try:
            logger.debug(f"Deleting plan that matches the id {plan_id} and etag {etag}")
            graph_helper: GraphHelper = GraphHelper()
            graph_helper.delete_request(
                f"/planner/plans/{plan_id}",
                {},
                {"If-Match": etag},
            )
        except AgendaException as e:
            logger.error(f"Error deleting plan: {e}")
