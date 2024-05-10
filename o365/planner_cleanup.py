from loguru import logger
from datetime import date
from o365.auth.auth_helper import AuthHelper
from o365.exception.agenda_exception import AgendaException
from o365.graph.graph_helper import GraphHelper
from o365.planner.planner_helper import PlannerHelper
from o365.util.constants import Constants
from o365.util.date_util import DateUtil


class PlannerCleanup:
    """This class is used for planner cleanup tasks"""

    _graph_client = None
    _last_month_first_day: date
    _group_id: str
    _last_month_weekly_meeting_signup: str

    def __init__(self, last_month_first_day: date = None):
        self._graph_client = AuthHelper.graph_service_client_with_adapter()
        self._group_id = Constants.GROUP_IDS[0]
        date_util = DateUtil()
        if last_month_first_day is None:
            self._last_month_first_day = date_util.last_month_date
        else:
            self._next_month_first_day = last_month_first_day
        self._last_month_weekly_meeting_signup = f"{self._last_month_first_day.strftime('%b')} - Weekly Meeting Signup"

    def cleanup(self, plan_names: list = []):
        """Cleanup the specified plans"""
        plan_names.append(self._last_month_weekly_meeting_signup)
        for plan_name in plan_names:
            logger.info(f"Deleting plan with name {plan_name}")
            plan = PlannerHelper.get_plan_by_name(self._graph_client, self._group_id, plan_name)
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
            # messages = graph_helper.delete_request(
            #     f"/planner/plans/{plan_id}",
            #     {},
            #     {"If-Match": etag},
            # )
            # if messages and messages["id"] is not None:
            #     logger.debug(messages["id"])
            #     return messages["id"]
        except AgendaException as e:
            logger.error(f"Error updating message on teams: {e}")
        return None
