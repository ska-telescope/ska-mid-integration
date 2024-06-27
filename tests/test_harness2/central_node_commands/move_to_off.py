"""A command to move the central node to off."""

from tango import DevState

from tests.test_harness2.command_mechanism.command import TestHarnessCommand
from tests.test_harness2.command_mechanism.state_change_waiter import (
    ExpectedStateChange,
)
from tests.test_harness2.sys_components.csp_wrapper import CSPWrapper
from tests.test_harness2.sys_components.dishes_wrapper import DishesWrapper
from tests.test_harness2.sys_components.sdp_wrapper import SDPWrapper
from tests.test_harness2.sys_components.tmc_wrapper import TMCWrapper
from tests.test_harness2.utils.enums import DishMode


class MoveToOffCommand(TestHarnessCommand):
    """A command to move the central node to off."""

    def __init__(
        self,
        tmc: TMCWrapper,
        csp: CSPWrapper,
        sdp: SDPWrapper,
        dishes: DishesWrapper,
    ):
        super().__init__()

        self.tmc = tmc
        self.csp = csp
        self.sdp = sdp
        self.dishes = dishes

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
