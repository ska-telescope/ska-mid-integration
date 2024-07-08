"""A wrapper for an emulated CSP."""

from tango import DevState

from tests.test_harness3.telescope_structure.csp_devices import CSPDevices
from tests.test_harness3.utils.emulated_teardown import (
    clear_command_call,
    reset_health_state,
    reset_transitions_data,
)


class EmulatedCSPDevices(CSPDevices):
    """A wrapper for an emulated CSP."""

    def move_to_on(self) -> None:
        # NOTE: in old code this line was AFTER
        # self.central_node.TelescopeOn(). Empirically,
        # it seems the order not to matter, but I am not sure.
        self.csp_subarray.SetDirectState(DevState.ON)

    def move_to_off(self) -> None:
        self.csp_subarray.SetDirectState(DevState.OFF)

    def clear_command_call(self) -> None:
        """Clear the command call on the CSP."""
        clear_command_call([self.csp_subarray])

    def reset_transitions_data(self) -> None:
        """Reset the transitions data on the CSP."""
        reset_transitions_data([self.csp_subarray])

    def reset_health_state(self) -> None:
        """Reset the health state on the CSP."""
        reset_health_state([self.csp_master, self.csp_subarray])
