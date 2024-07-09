"""A wrapper for TMC and all integration tests sub-components."""

from dataclasses import dataclass

from tests.test_harness3.helpers import check_subarray_obs_state
from tests.test_harness3.telescope_structure.csp_devices import CSPDevices
from tests.test_harness3.telescope_structure.dishes_devices import (
    DishesDevices,
)
from tests.test_harness3.telescope_structure.sdp_devices import SDPDevices
from tests.test_harness3.telescope_structure.tmc_devices import TMCDevices


@dataclass
class TelescopeWrapper:  # pylint: disable=too-many-public-methods
    """A wrapper class to implement common tango specific details
    and standard set of commands for TMC Mid CentralNode,
    defined by the SKA Control Model.
    TODO: re-write contract."""

    tmc: TMCDevices
    sdp: SDPDevices
    csp: CSPDevices
    dishes: DishesDevices

    def tear_down(self) -> None:
        """Tear down the entire telescope test structure."""
        self.tmc.tear_down()
        self.sdp.tear_down()
        self.csp.tear_down()
        self.dishes.tear_down()
        assert check_subarray_obs_state("EMPTY")

    def clear_command_call(self) -> None:
        """Clear the command call on the telescope (if needed)."""
        self.sdp.clear_command_call()
        self.csp.clear_command_call()
        self.dishes.clear_command_call()
