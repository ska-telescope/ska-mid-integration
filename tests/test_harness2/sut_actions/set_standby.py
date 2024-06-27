"""An action to set the central node to STANDBY State."""

import logging

from tango import DevState

from tests.test_harness2.sut_structure.sut_action import SUTAction
from tests.test_harness2.utils.enums import DishMode
from tests.test_harness2.utils.state_change_waiter import ExpectedStateChange

LOGGER = logging.getLogger(__name__)


class SetStandby(SUTAction):
    """An action to set the central node to STANDBY State."""

    def _action(self):
        LOGGER.info("Setting the central node to STANDBY state")

        self.tmc.set_central_node_to_standby()
        self.csp.move_to_off()

    def expected_outcome(self):
        res = [
            ExpectedStateChange(self.sdp.sdp_subarray, "State", DevState.OFF),
            ExpectedStateChange(
                self.sdp.sdp_master, "State", DevState.STANDBY
            ),
            ExpectedStateChange(self.csp.csp_subarray, "State", DevState.OFF),
            ExpectedStateChange(
                self.csp.csp_master, "State", DevState.STANDBY
            ),
        ]

        res += [
            ExpectedStateChange(dish, "dishMode", DishMode.STANDBY_LP)
            for dish in self.dishes.dish_master_list
        ]

        return res
