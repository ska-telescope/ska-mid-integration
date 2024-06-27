"""An action to move the central node to off."""

from tango import DevState

from tests.test_harness2.command_mechanism.state_change_waiter import (
    ExpectedStateChange,
)
from tests.test_harness2.sut_structure.sut_action import SUTAction
from tests.test_harness2.utils.enums import DishMode


class MoveToOff(SUTAction):
    """An action to move the central node to off."""

    def _action(self):
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
