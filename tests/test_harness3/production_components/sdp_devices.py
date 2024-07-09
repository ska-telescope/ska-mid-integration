"""A wrapper for a production SDP."""

from tests.test_harness3.telescope_structure.sdp_devices import SDPDevices


class ProductionSDPDevices(SDPDevices):
    """A wrapper for a production SDP."""

    def tear_down(self) -> None:
        """Tear down the CSP (not needed)."""
        pass

    def clear_command_call(self) -> None:
        """Clear the command call on the SDP (not needed)."""
        pass
