"""A wrapper for TMC and all integration tests sub-components."""

from dataclasses import dataclass

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

    tmc_wrapper: TMCDevices
    sdp_wrapper: SDPDevices
    csp_wrapper: CSPDevices
    dishes_wrapper: DishesDevices
