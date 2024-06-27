"""A wrapper for an emulated SDP."""

from tests.test_harness2.sut_structure.sdp_wrapper import SDPWrapper
from tests.test_harness2.utils.emulated_teardown import (
    clear_command_call,
    reset_health_state,
    reset_transitions_data,
)


class EmulatedSDPWrapper(SDPWrapper):
    """A wrapper for an emulated SDP."""

    def tear_down(self) -> None:
        """Tear down the an emulated SDP."""
        reset_health_state([self.sdp_master])
        clear_command_call([self.sdp_subarray])
        reset_transitions_data([self.sdp_subarray])
