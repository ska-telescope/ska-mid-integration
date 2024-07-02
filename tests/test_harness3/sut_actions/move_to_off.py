"""An action to move the central node to OFF State."""

import logging

from tango import DevState

from tests.test_harness3.sut_structure.sut_action import SUTAction
from tests.test_harness3.utils.enums import DishMode
from tests.test_harness3.utils.state_change_waiter import ExpectedStateChange

LOGGER = logging.getLogger(__name__)


class MoveToOff(SUTAction):
    """An action to move the central node to off."""

    def _action(self):
        LOGGER.info("Moving the central node to OFF state")

        self.tmc.move_central_node_to_off()
        self.csp.move_to_off()

    def expected_outcome(self):
        res = [
            ExpectedStateChange(self.sdp.sdp_subarray, "State", DevState.OFF),
            ExpectedStateChange(self.sdp.sdp_master, "State", DevState.OFF),
            ExpectedStateChange(self.csp.csp_subarray, "State", DevState.OFF),
            ExpectedStateChange(self.csp.csp_master, "State", DevState.OFF),
        ]

        res += [
            ExpectedStateChange(dish, "dishMode", DishMode.STANDBY_LP)
            for dish in self.dishes.dish_master_list
        ]

        return res
