"""Testing the Science Scan after a five point calibration scan"""
import json

import pytest
from pytest_bdd import given, scenario, then, when
from ska_control_model import ObsState

from tests.resources.test_harness.constant import (
    DISH_001_CALIBRATION_DATA,
    DISH_036_CALIBRATION_DATA,
)
from tests.resources.test_harness.helpers import (
    check_long_running_command_status_events,
    check_subarray_obs_state,
    get_device_simulators,
    prepare_json_args_for_commands,
    wait_and_validate_device_attribute_value,
)
from tests.resources.test_harness.utils.enums import SimulatorDeviceType


@pytest.mark.SKA_mid
@scenario(
    "../features/test_harness/science_scan_after_calibration_scan.feature",
    "TMC behaviour during a science scan after a five point calibration scan.",
)
def test_science_scan_after_five_point_calibration_scan():
    """
    Test case to verify the Science scan functionality after a five point
    calibration scan on TMC
    """


@given("a TMC")
def given_tmc(subarray_node, event_recorder):
    """Given a TMC"""
    event_recorder.subscribe_event(subarray_node.subarray_node, "obsState")
    for dish_master in subarray_node.dish_master_list[:2]:
        event_recorder.subscribe_event(dish_master, "longRunningCommandStatus")
    subarray_node.move_to_on()
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.EMPTY,
    )


@given("a subarray post five point calibration")
def a_subarray_after_five_point_calibration(
    subarray_node, event_recorder, simulator_factory, command_input_factory
):
    """Given a Subarray after the five point Calibration scan."""
    csp_sim, sdp_sim, _, _, _, _ = get_device_simulators(simulator_factory)

    event_recorder.subscribe_event(csp_sim, "obsState")
    event_recorder.subscribe_event(sdp_sim, "obsState")
    event_recorder.subscribe_event(subarray_node.subarray_node, "obsState")
    subarray_node.force_change_of_obs_state("READY")
    assert event_recorder.has_change_event_occurred(
        csp_sim,
        "obsState",
        ObsState.READY,
    )
    assert event_recorder.has_change_event_occurred(
        sdp_sim,
        "obsState",
        ObsState.READY,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.READY,
    )

    scan_command_input = prepare_json_args_for_commands(
        "scan_mid", command_input_factory
    )
    subarray_node.execute_transition("Scan", scan_command_input)
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.SCANNING,
        lookahead=15,
    )
    assert check_subarray_obs_state("READY", 500)

    scan_jsons = ["scan_mid" for _ in range(4)]
    partial_configuration_jsons = [
        f"partial_configure_{i}" for i in range(1, 5)
    ]

    subarray_node.execute_five_point_calibration_scan(
        partial_configuration_jsons,
        scan_jsons,
        event_recorder,
        command_input_factory,
    )


@when("I invoke Configure command for a science scan")
def configure_for_science_scan(
    subarray_node, simulator_factory, command_input_factory
):
    """When Configure is invoked for a Science Scan."""
    configure_command_input = prepare_json_args_for_commands(
        "configure_mid", command_input_factory
    )
    subarray_node.execute_transition("Configure", configure_command_input)
    sdp_sim = simulator_factory.get_or_create_simulator_device(
        SimulatorDeviceType.MID_SDP_DEVICE
    )
    subarray_node.simulate_receive_addresses_event(
        sdp_sim, command_input_factory
    )


@then(
    "the subarray fetches calibration solutions from SDP and applies them to "
    + "the Dishes"
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

    assert wait_and_validate_device_attribute_value(
        subarray_node.dish_leaf_node_list[0],
        "lastPointingData",
        json.dumps(DISH_001_CALIBRATION_DATA),
        is_json=True,
        timeout=30,
    )
    assert wait_and_validate_device_attribute_value(
        subarray_node.dish_leaf_node_list[1],
        "lastPointingData",
        json.dumps(DISH_036_CALIBRATION_DATA),
        is_json=True,
        timeout=30,
    )


@then("is in READY obsState")
def subarray_is_in_ready_obsstate():
    """Subarray is in READY obsState."""
    assert check_subarray_obs_state("READY", 500)
