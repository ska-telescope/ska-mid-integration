"""A test wrapper for the SDP."""

import abc

from tango import DeviceProxy

from tests.test_harness3.telescope_config.components_config import (
    SDPConfiguration,
)
from tests.test_harness3.telescope_config.configuration_factory import (
    TestHarnessConfigurationFactory,
)

emulation_configuration = (
    TestHarnessConfigurationFactory().emulation_configuration
)


class SDPDevices(abc.ABC):
    """A test wrapper for the SDP."""

    def __init__(self, sdp_configuration: SDPConfiguration):
        """Initialize the SDP wrapper."""
        self.sdp_master = DeviceProxy(sdp_configuration.sdp_master_name)
        self.sdp_subarray = DeviceProxy(sdp_configuration.sdp_subarray1_name)

    def set_subarray_id(self, subarray_id: str) -> None:
        """Set the subarray ID on the SDP subarray."""
        subarray_id = str(subarray_id).zfill(2)
        self.sdp_subarray = DeviceProxy(f"mid-sdp/subarray/{subarray_id}")

    def tear_down(self) -> None:
        """Tear down the SDP."""
        self.reset_health_state()
        self.clear_command_call()
        self.reset_transitions_data()
        self.reset_delay()

    @abc.abstractmethod
    def clear_command_call(self) -> None:
        """Clear the command call on the SDP (if needed)."""
        pass

    @abc.abstractmethod
    def reset_transitions_data(self) -> None:
        """Reset the transitions data on the SDP (if needed)."""
        pass

    @abc.abstractmethod
    def reset_health_state(self) -> None:
        """Reset the health state on the SDP (if needed)."""
        pass

    @abc.abstractmethod
    def reset_delay(self) -> None:
        """Reset the delay on the SDP (if needed)."""
        pass
