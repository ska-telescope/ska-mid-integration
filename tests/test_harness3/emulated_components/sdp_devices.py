"""A wrapper for an emulated SDP."""

import json

from tests.test_harness3.telescope_structure.sdp_devices import SDPDevices
from tests.test_harness3.utils.emulated_teardown import (
    clear_command_call,
    reset_delay,
    reset_health_state,
    reset_transitions_data,
)


class EmulatedSDPDevices(SDPDevices):
    """A wrapper for an emulated SDP."""

    def tear_down(self) -> None:
        super().tear_down()
        self.sdp_subarray.SetDefective(json.dumps({"enabled": False}))

    def clear_command_call(self) -> None:
        """Clear the command call on the SDP."""
        clear_command_call([self.sdp_subarray])

    def reset_transitions_data(self) -> None:
        """Reset the transitions data on the SDP."""
        reset_transitions_data([self.sdp_subarray])

    def reset_health_state(self) -> None:
        """Reset the health state on the SDP."""
        reset_health_state([self.sdp_master, self.sdp_subarray])

    def reset_delay(self) -> None:
        """Reset the delay on the SDP."""
        reset_delay([self.sdp_subarray])
