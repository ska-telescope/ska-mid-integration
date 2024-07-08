"""A wrapper for a production SDP."""

from tests.test_harness3.telescope_structure.sdp_devices import SDPDevices


class ProductionSDPDevices(SDPDevices):
    """A wrapper for a production SDP."""

    def clear_command_call(self) -> None:
        """Clear the command call on the SDP (not needed)."""
        pass

    def reset_transitions_data(self) -> None:
        """Reset the transitions data on the SDP (not needed)."""
        pass

    def reset_health_state(self) -> None:
        """Reset the health state on the SDP (not needed)."""
        pass
