"""Pytest BDD step implementations specific to tmc integration
tests."""


# import json
import logging

from pytest_bdd import given

# from ska_control_model import ObsState
from ska_ser_logging import configure_logging
from tango import DevState

# from tests.resources.test_harness.helpers import (
#     check_subarray_instance,
#     prepare_json_args_for_centralnode_commands,
#     prepare_json_args_for_commands,
#     update_scan_id,
#     update_scan_type,
# )
# from tests.resources.test_harness.utils.common_utils import (
#     check_configure_successful,
#     check_obsstate_sdp_in_first_configure,
#     check_scan_successful,
#     wait_added_for_skb372,
# )
# from tests.resources.test_support.common_utils.result_code import ResultCode

configure_logging(logging.DEBUG)
LOGGER = logging.getLogger(__name__)


@given("the telescope is in ON state")
def given_a_telescope_in_on_state(central_node_mid, event_recorder):
    """Checks if CentralNode's telescopeState attribute value is on."""

    event_recorder.subscribe_event(
        central_node_mid.central_node, "telescopeState"
    )
    central_node_mid.move_to_on()
    event_recorder.subscribe_event(central_node_mid.csp_master, "State")
    event_recorder.subscribe_event(
        central_node_mid.subarray_devices["csp_subarray"], "State"
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.csp_master,
        "State",
        DevState.ON,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.subarray_devices["csp_subarray"],
        "State",
        DevState.ON,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "telescopeState",
        DevState.ON,
    )
