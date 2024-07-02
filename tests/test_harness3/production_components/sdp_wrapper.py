"""A wrapper for a production SDP."""

from tests.test_harness3.sut_structure.sdp_wrapper import SDPWrapper


class ProductionSDPWrapper(SDPWrapper):
    """A wrapper for a production SDP."""

    def tear_down(self) -> None:
        """Tear down the a production SDP  does nothing."""
        pass
