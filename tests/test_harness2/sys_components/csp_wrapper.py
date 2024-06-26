"""A test wrapper for the CSP."""

import abc

from tango import DeviceProxy

from tests.test_harness2.config.test_wrappers_configurations import (
    CSPConfiguration,
)


class CSPWrapper(abc.ABC):
    """A test wrapper for the CSP."""

    def __init__(self, csp_configuration: CSPConfiguration):
        """Initialize the CSP wrapper."""
        self.csp_master = DeviceProxy(csp_configuration.csp_master_name)
        self.csp_subarray = DeviceProxy(csp_configuration.csp_subarray1_name)

    # NOTE: this is not that much a real "move_to_on" command, instead
    # it seems to be "an action that must be done when on TMC central node
    # is called a move_to_on command". This is a detail, but I guess this
    # is important to think about a different more event or command oriented
    # design.
    @abc.abstractmethod
    def move_to_on(self) -> None:
        """Move the CSP to the ON state."""
        pass

    @abc.abstractmethod
    def move_to_off(self) -> None:
        """Move the CSP to the OFF state."""
        pass

    @abc.abstractmethod
    def tear_down(self) -> None:
        """Tear down the CSP."""
        pass

    def set_subarray_id(self, subarray_id: str) -> None:
        """Set the subarray ID on the CSP subarray."""
        subarray_id = str(subarray_id).zfill(2)
        self.csp_subarray = DeviceProxy(f"mid-csp/subarray/{subarray_id}")
