"""Test common"""
import logging

from pytest_bdd import given  # , parsers, scenario, then, when
from ska_ser_logging import configure_logging
from tango import DevState

configure_logging(logging.DEBUG)
LOGGER = logging.getLogger(__name__)


@given("Telescope is ON state")
def given_a_tmc(central_node_mid, event_recorder, subarray_node):
    """A method to define TMC and SDP and subscribe ."""
    assert central_node_mid.central_node.ping() > 0
    assert central_node_mid.subarray_devices["sdp_subarray"].ping() > 0
    event_recorder.subscribe_event(
        central_node_mid.central_node, "telescopeState"
    )
    event_recorder.subscribe_event(
        subarray_node.subarray_devices.get("sdp_subarray"), "obsState"
    )

    event_recorder.subscribe_event(
        subarray_node.subarray_devices.get("csp_subarray"), "obsState"
    )
    event_recorder.subscribe_event(subarray_node.subarray_node, "obsState")
    event_recorder.subscribe_event(
        subarray_node.subarray_devices["sdp_subarray"], "scanID"
    )
    event_recorder.subscribe_event(
        subarray_node.subarray_devices["sdp_subarray"], "scanType"
    )

    event_recorder.subscribe_event(
        subarray_node.subarray_node, "longRunningCommandResult"
    )
    central_node_mid.move_to_on()

    assert event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "telescopeState",
        DevState.ON,
    )
    LOGGER.info("On step completed")
