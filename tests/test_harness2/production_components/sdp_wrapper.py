"""A wrapper for a production SDP."""

from tests.test_harness2.sys_components.sdp_wrapper import SDPWrapper


class ProductionSDPWrapper(SDPWrapper):
    """A wrapper for a production SDP."""

    def tear_down(self) -> None:
        """Tear down the a production SDP  does nothing."""
        pass
