"""A facade to expose the SDP devices to the tests."""


from tests.test_harness3.telescope_structure.telescope_wrapper import (
    TelescopeWrapper,
)


class SDPFacade:
    """A facade to expose the SDP devices to the tests."""

    def __init__(self, telescope: TelescopeWrapper) -> None:
        self._telescope = telescope

    @property
    def sdp_master(self):
        """A Tango proxy to the SDP master device."""
        return self._telescope.sdp.sdp_master

    @property
    def sdp_subarray(self):
        """A Tango proxy to the SDP subarray device."""
        return self._telescope.sdp.sdp_subarray
