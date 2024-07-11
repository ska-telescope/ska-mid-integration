"""An action to move the central node to OFF State."""

import logging

from tango import DevState

from tests.test_harness3.telescope_actions.state_change_waiter import (
    ExpectedStateChange,
)
from tests.test_harness3.telescope_actions.telescope_action import (
    TelescopeAction,
)
from tests.test_harness3.utils.enums import DishMode

LOGGER = logging.getLogger(__name__)


class MoveToOff(TelescopeAction):
    """An action to move the central node to off."""

    def _action(self):
        LOGGER.info("Moving the central node to OFF state")

        self.telescope.tmc.central_node.TelescopeOff()
        self.telescope.csp.move_to_off()

    def termination_condition(self):
        res = [
            ExpectedStateChange(
                self.telescope.sdp.sdp_subarray, "State", DevState.OFF
            ),
            ExpectedStateChange(
                self.telescope.sdp.sdp_master, "State", DevState.OFF
            ),
            ExpectedStateChange(
                self.telescope.csp.csp_subarray, "State", DevState.OFF
            ),
            ExpectedStateChange(
                self.telescope.csp.csp_master, "State", DevState.OFF
            ),
        ]

        res += [
            ExpectedStateChange(dish, "dishMode", DishMode.STANDBY_LP)
            for dish in self.telescope.dishes.dish_master_list
        ]

        return res
