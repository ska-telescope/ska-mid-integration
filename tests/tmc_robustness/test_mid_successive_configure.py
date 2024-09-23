"""Test case to verify SKB-467"""

import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_tango_base.control_model import ObsState
from tango import DevState

from tests.resources.test_harness.helpers import (
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
)


@pytest.mark.SKA_mid_skip
@scenario(
    "../features/successive_configure.feature",
    "TMC validates reconfigure functionality",
)
def test_multiple_configure_functionality():
    """
    Test TMC allows multiple configuration
    """


@given("the TMC is On")
def given_tmc(central_node_mid, event_recorder):
    event_recorder.subscribe_event(
        central_node_mid.central_node, "telescopeState"
    )

    if central_node_mid.telescope_state != "ON":
        central_node_mid.move_to_on()

    assert event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "telescopeState",
        DevState.ON,
    )


@given("the subarray is in IDLE obsState")
def given_subarray_in_idle(
    subarray_node, central_node_mid, event_recorder, command_input_factory
):
    """Method to check subarrays is in IDLE obsstate"""
    event_recorder.subscribe_event(subarray_node.subarray_node, "obsState")
    event_recorder.subscribe_event(
        subarray_node.subarray_devices.get("sdp_subarray"), "obsState"
    )
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_mid", command_input_factory
    )
    central_node_mid.store_resources(assign_input_json)
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.IDLE,
    )


@when(parsers.parse("the command configure is issued with {input_json1}"))
def send_configure(subarray_node, command_input_factory, input_json1):
    input_json = prepare_json_args_for_commands(
        input_json1, command_input_factory
    )
    subarray_node.store_configuration_data(input_json)


@when(
    parsers.parse(
        "the next successive configure command is issued with {input_json2}"
    )
)
def send_next_configure(subarray_node, command_input_factory, input_json2):
    input_json = prepare_json_args_for_commands(
        input_json2, command_input_factory
    )
    subarray_node.store_configuration_data(input_json)


@then("the subarray reconfigures changing its obsState to READY")
@then("the subarray transitions to obsState READY")
def check_for_reconfigure_ready(subarray_node, event_recorder):
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.READY,
    )
