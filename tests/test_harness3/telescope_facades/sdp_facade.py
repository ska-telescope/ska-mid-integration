"""A facade to expose the SDP devices to the tests."""


from tests.test_harness3.telescope_actions.sdp_subarray.subarray_simulate_receive_addresses import (  # pylint: disable=line-too-long # noqa E501
    SubarraySimulateReceiveAddresses,
)
from tests.test_harness3.telescope_inputs.json_input import JSONInput
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

    def simulate_receive_addresses_event(
        self,
        sdp_sim,  # TODO: remove
        receive_addresses_input: JSONInput,
    ):
        """Set SDP Subarray's receive addresses for Subarray Node processing.

        :param sdp_sim: The SDP simulator.
        :param command_input_factory: The command input factory.
        """
        # Call this with a FileJSONInput('subarray', 'receive_addresses_mid')
        # instance as the second argument.
        SubarraySimulateReceiveAddresses(
            sdp_sim, receive_addresses_input
        ).execute()
