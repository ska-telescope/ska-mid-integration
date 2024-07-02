"""A wrapper for an emulated CSP."""

from tango import DevState

from tests.test_harness3.sut_structure.csp_wrapper import CSPWrapper
from tests.test_harness3.utils.emulated_teardown import (
    clear_command_call,
    reset_health_state,
    reset_transitions_data,
)


class EmulatedCSPWrapper(CSPWrapper):
    """A wrapper for an emulated CSP."""

    def move_to_on(self) -> None:
        # NOTE: in old code this line was AFTER
        # self.central_node.TelescopeOn(). Empirically,
        # it seems the order not to matter, but I am not sure.
        self.csp_subarray.SetDirectState(DevState.ON)

    def move_to_off(self) -> None:
        self.csp_subarray.SetDirectState(DevState.OFF)

    def tear_down(self) -> None:
        # self.move_to_off()
        # NOTE: reset health state just to csp_master?
        # Why not to csp_subarray1?
        reset_health_state([self.csp_master])

        # NOTE: why just to csp_subarray1 and not to csp_master?
        clear_command_call([self.csp_subarray])

        # NOTE: why just to csp_subarray1 and not to csp_master?
        reset_transitions_data([self.csp_subarray])

        # NOTE: similar tear down operations are done in SubarrayNodeWrapper
        # too. What is the difference between them? Can we unify them?
