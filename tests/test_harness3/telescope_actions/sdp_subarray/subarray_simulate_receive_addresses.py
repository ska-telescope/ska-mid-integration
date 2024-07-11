"""Sets the receive addresses attribute on SDP Subarray so an event can
be simulated for Subarray Node to process.
"""

import msgpack
import msgpack_numpy
from tango import DeviceProxy

from tests.test_harness3.helpers import prepare_json_args_for_commands
from tests.test_harness3.telescope_actions.telescope_action import (
    TelescopeAction,
)
from tests.test_harness3.telescope_config.configuration_factory import (
    TestHarnessConfigurationFactory,
)
from tests.test_harness3.telescope_config.hardcoded_values import (
    HardcodedValues,
)


class SubarraySimulateReceiveAddresses(TelescopeAction):
    """Sets the receive addresses attribute on SDP Subarray so an event can
    be simulated for Subarray Node to process.
    """

    def __init__(self, sdp_sim, command_input_factory):
        super().__init__()
        self.sdp_sim = sdp_sim
        self.command_input_factory = command_input_factory

    def _action(self):
        receive_addresses = prepare_json_args_for_commands(
            "receive_addresses_mid", self.command_input_factory
        )

        # TODO: change with a ref to some SDP device
        self.sdp_sim.SetDirectreceiveAddresses(receive_addresses)

        # Setting pointing offsets after encoding the data.
        sdp_qc = DeviceProxy(
            TestHarnessConfigurationFactory()
            .get_other_configurations()
            .sdp_queue_connector
        )
        encoded_data = msgpack.packb(
            HardcodedValues().pointing_offsets, default=msgpack_numpy.encode
        )
        sdp_qc.SetDirectPointingOffsets(("msgpack_numpy", encoded_data))

    def termination_condition(self):
        return []
