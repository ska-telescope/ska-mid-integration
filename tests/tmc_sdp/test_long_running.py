"""Test TMC-SDP Long Sequence  functionality"""

import json
import logging

import pytest
from pytest_bdd import given, parsers, scenario, when  # then
from ska_control_model import ObsState
from ska_ser_logging import configure_logging
from tango import DevState

from tests.resources.test_harness.helpers import (
    check_subarray_instance,
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
    update_json,
)

configure_logging(logging.DEBUG)
LOGGER = logging.getLogger(__name__)


@pytest.mark.trupti
@pytest.mark.tmc_sdp
@scenario(
    "../features/tmc_sdp/long_running.feature",
    "TMC executes long sequence of commands successfully",
)
def test_tmc_sdp_long_sequences():
    """
    Test case to verify TMC-SDP  functionality with long sequences of commands
    """


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

    central_node_mid.move_to_on()

    assert event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "telescopeState",
        DevState.ON,
    )
    LOGGER.info("On step completed")


@when(parsers.parse("I assign resources to TMC SubarrayNode {subarray_id}"))
def telescope_is_in_idle_state(
    central_node_mid,
    event_recorder,
    command_input_factory,
    subarray_id,
    subarray_node,
):
    """A method to move subarray into the IDLE ObsState."""

    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_mid_multiple_scantype", command_input_factory
    )

    assign_str = json.loads(assign_input_json)
    # Here we are adding this to get an event of ObsState CONFIGURING from SDP
    # Subarray
    assign_str["sdp"]["processing_blocks"][0]["parameters"][
        "time-to-ready"
    ] = 2

    central_node_mid.store_resources(json.dumps(assign_str))

    check_subarray_instance(
        subarray_node.subarray_devices.get("sdp_subarray"), subarray_id
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_devices.get("sdp_subarray"),
        "obsState",
        ObsState.IDLE,
    )

    check_subarray_instance(subarray_node.subarray_node, subarray_id)
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.IDLE,
    )
    LOGGER.info("Assign resources  completed")


@when(
    parsers.parse(
        "configure and scan TMC SubarrayNode {subarray_id} "
        "for each {scan_types} and {scan_ids}"
    )
)
def execute_initial_configure_command(
    subarray_node,
    command_input_factory,
    scan_ids,
    event_recorder,
    subarray_id,
    scan_types,
):
    """ "A method to invoke configure command"""

    check_subarray_instance(subarray_node.subarray_node, subarray_id)
    configure_json = prepare_json_args_for_commands(
        "sdp_mid_configure1", command_input_factory
    )

    my_list = eval(scan_types)
    LOGGER.info(f"working on scan types {my_list} {scan_ids}")
    # scan_type_key_path = '["sdp"]["scan_type"]'

    for scan_type in my_list:
        LOGGER.info(f" scan_type is {scan_type}")
        configure_json = update_json(configure_json, scan_type)
        subarray_node.store_configuration_data(configure_json)
        # assert event_recorder.has_change_event_occurred(
        #     subarray_node.subarray_devices["sdp_subarray"],
        #     "obsState",
        #     ObsState.CONFIGURING,
        # )
        assert event_recorder.has_change_event_occurred(
            subarray_node.subarray_devices["sdp_subarray"],
            "obsState",
            ObsState.READY,
        )

    LOGGER.info("Configure Completed")


# @when("the subarray transitions to obsState READY")
# def check_subarray_in_ready(subarray_node, event_recorder):
#     """A method to check SDP subarray obsstate"""
#
#     assert event_recorder.has_change_event_occurred(
#         subarray_node.subarray_devices["sdp_subarray"],
#         "obsState",
#         ObsState.READY,
#     )
#     assert event_recorder.has_change_event_occurred(
#         subarray_node.subarray_devices["csp_subarray"],
#         "obsState",
#         ObsState.READY,
#     )
#     assert event_recorder.has_change_event_occurred(
#         subarray_node.subarray_node,
#         "obsState",
#         ObsState.READY,
#     )
#
#
# @when(
#     parsers.parse(
#         "the next successive configure command is issued with {input_json2}"
#     )
# )
# def execute_next_configure_command(
#     subarray_node, command_input_factory, input_json2
# ):
#     """ "A method to invoke configure command"""
#
#     configure_json = prepare_json_args_for_commands(
#         input_json2, command_input_factory
#     )
#     subarray_node.store_configuration_data(configure_json)
#
#     # TODO :: Issue is raised with SDP team , awating for
#     #  confirmation to raise it as bug
#     # assert event_recorder.has_change_event_occurred(
#     #     subarray_node.subarray_devices["sdp_subarray"],
#     #     "obsState",
#     #     ObsState.CONFIGURING,
#     # )
#
#
# @then(
#     parsers.parse(
#         "the subarray {subarray_id} reconfigures changing its "
#         "obsState to READY"
#     )
# )
# def check_subarray_in_ready_in_reconfigure(
#     central_node_mid, subarray_node, event_recorder, subarray_id
# ):
#     """A method to check SDP subarray obsstate"""
#
#     # TODO :: Issue is raised with SDP team ,
#     #  awating for confirmation to raise it as bug
#     # check_subarray_instance(
#     #     central_node_mid.subarray_devices.get("sdp_subarray"), subarray_id
#     # )
#     #
#     # assert event_recorder.has_change_event_occurred(
#     #     subarray_node.subarray_devices["sdp_subarray"],
#     #     "obsState",
#     #     ObsState.READY,
#     # )
#
#     check_subarray_instance(central_node_mid.subarray_node, subarray_id)
#     assert event_recorder.has_change_event_occurred(
#         subarray_node.subarray_node,
#         "obsState",
#         ObsState.READY,
#     )
