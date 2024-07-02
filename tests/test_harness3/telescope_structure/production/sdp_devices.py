"""A wrapper for a production SDP."""

from tests.test_harness3.telescope_structure.sdp_devices import SDPDevices


class ProductionSDPDevices(SDPDevices):
    """A wrapper for a production SDP."""

    def tear_down(self) -> None:
        """Tear down the a production SDP  does nothing."""
        pass
