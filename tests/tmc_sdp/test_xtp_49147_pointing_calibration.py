"""Testing the Science Scan after a five point calibration scan"""
import json

import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState
from tango import DevState

from tests.resources.test_harness.helpers import (
    check_long_running_command_status_events,
    check_subarray_obs_state,
    get_device_simulators,
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
    wait_for_last_pointing_data,
)
from tests.resources.test_support.common_utils.result_code import ResultCode


@pytest.mark.tmc_sdp
@pytest.mark.pointing_cal
@scenario(
    "../features/tmc_sdp/xtp_49147_pointing_calibration_five_point.feature",
    "TMC is able to process pointing calibration received from SDP during "
    "five point calibration scan.",
)
def test_pointing_calibration_during_five_point_scan():
    """
    Test case to verify the Science scan functionality after a five point
    calibration scan on TMC
    """


@given("a TMC")
def given_tmc(central_node_mid, subarray_node, event_recorder):
    """Given a TMC"""
    event_recorder.subscribe_event(
        central_node_mid.central_node, "telescopeState"
    )
    event_recorder.subscribe_event(central_node_mid.sdp_master, "State")
    event_recorder.subscribe_event(
        central_node_mid.subarray_devices["sdp_subarray"], "State"
    )
    event_recorder.subscribe_event(subarray_node.subarray_node, "obsState")
    for dish_master in subarray_node.dish_master_list[:2]:
        event_recorder.subscribe_event(dish_master, "longRunningCommandStatus")

    central_node_mid.move_to_on()

    assert event_recorder.has_change_event_occurred(
        central_node_mid.sdp_master,
        "State",
        DevState.ON,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.subarray_devices["sdp_subarray"],
        "State",
        DevState.ON,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "telescopeState",
        DevState.ON,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.EMPTY,
    )


@when("I assign resources for five point calibration scan")
def assign_resource_for_five_point_calibration(
    central_node_mid,
    subarray_node,
    event_recorder,
    simulator_factory,
    command_input_factory,
):
    """Given a Subarray after the five point Calibration scan."""
    csp_sim, _, _, _, _, _ = get_device_simulators(simulator_factory)

    event_recorder.subscribe_event(csp_sim, "obsState")
    event_recorder.subscribe_event(subarray_node.subarray_node, "obsState")
    event_recorder.subscribe_event(
        central_node_mid.subarray_devices.get("sdp_subarray"), "obsState"
    )
    event_recorder.subscribe_event(
        subarray_node.subarray_node, "longRunningCommandResult"
    )
    event_recorder.subscribe_event(
        central_node_mid.central_node, "longRunningCommandResult"
    )

    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_five_point_sdp", command_input_factory
    )

    _, unique_id = central_node_mid.perform_action(
        "AssignResources", assign_input_json
    )

    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.IDLE,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.subarray_devices.get("sdp_subarray"),
        "obsState",
        ObsState.IDLE,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "longRunningCommandResult",
        (unique_id[0], str(int(ResultCode.OK))),
        lookahead=5,
    )


@when("I configure subarray for a calibration scan")
def configure_for_science_scan(subarray_node, command_input_factory):
    """When Configure is invoked for a Science Scan."""
    configure_command_input = prepare_json_args_for_commands(
        "configure_mid", command_input_factory
    )
    # Update scan type to pointing
    configure_json = json.loads(configure_command_input)
    configure_json["sdp"]["scan_type"] = "pointing"
    subarray_node.execute_transition("Configure", json.dumps(configure_json))
    assert check_subarray_obs_state("READY", 500)


@when(
    parsers.parse(
        "I invoke calibration scan five times with scan ids {scan_ids}"
    )
)
def invoke_scan_five_times(
    subarray_node, command_input_factory, event_recorder, scan_ids
):
    """Invoke Scan five times"""
    scan_id_list = scan_ids.split(",")
    scan_command_input = prepare_json_args_for_commands(
        "scan_mid", command_input_factory
    )
    scan_json_dict = json.loads(scan_command_input)
    for scan_id in scan_id_list:
        scan_json_dict["scan_id"] = int(scan_id)
        subarray_node.execute_transition("Scan", json.dumps(scan_json_dict))
        assert event_recorder.has_change_event_occurred(
            subarray_node.subarray_node,
            "obsState",
            ObsState.SCANNING,
            lookahead=15,
        )
        assert check_subarray_obs_state("READY", 600)


@then(
    "the TMC receive pointing calibration from SDP and applies them to the "
    + "Dishes"
)
def subarray_applies_calibration_solutions_to_dishes(
    subarray_node, event_recorder
):
    """Then the Subarray fetches and applies the configuration solutions to the
    dishes."""

    for dish_master in subarray_node.dish_master_list[:2]:
        check_long_running_command_status_events(
            event_recorder, dish_master, "TrackLoadStaticOff"
        )

    assert wait_for_last_pointing_data(
        subarray_node.dish_leaf_node_list[0],
    )
    assert wait_for_last_pointing_data(
        subarray_node.dish_leaf_node_list[1],
    )
