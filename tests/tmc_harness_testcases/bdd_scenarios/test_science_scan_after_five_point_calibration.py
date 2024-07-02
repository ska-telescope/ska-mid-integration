"""Testing the Science Scan after a five point calibration scan"""
import json

import pytest
from pytest_bdd import given, scenario, then, when
from ska_control_model import ObsState
from tango import DevState

from tests.resources.test_harness.constant import (
    DISH_001_CALIBRATION_DATA,
    DISH_036_CALIBRATION_DATA,
)
from tests.resources.test_harness.helpers import (
    check_subarray_obs_state,
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
    wait_and_validate_device_attribute_value,
)
from tests.resources.test_harness.utils.enums import SimulatorDeviceType
from tests.resources.test_support.common_utils.result_code import ResultCode
from tests.resources.test_support.enum import DishMode, PointingState


@pytest.mark.skip()
@pytest.mark.SKA_mid
@pytest.mark.tmc_dish
@scenario(
    "../features/test_harness/science_scan_after_calibration_scan.feature",
    "TMC Behavior During a Five-Point Calibration Scan",
)
def test_science_scan_after_five_point_calibration_scan():
    """
    Test case to verify the Science scan functionality after a five point
    calibration scan on TMC
    """


@given("a TMC")
def given_tmc(central_node_mid, subarray_node, event_recorder):
    """Given a TMC"""
    event_recorder.subscribe_event(subarray_node.subarray_node, "obsState")
    event_recorder.subscribe_event(
        central_node_mid.central_node, "telescopeState"
    )
    for dish_master in subarray_node.dish_master_list:
        event_recorder.subscribe_event(dish_master, "dishMode")
    central_node_mid.move_to_on()
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.EMPTY,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "telescopeState",
        DevState.ON,
    )


@when("five point calibration scan performed on given subarray")
def a_subarray_after_five_point_calibration(
    central_node_mid,
    subarray_node,
    event_recorder,
    simulator_factory,
    command_input_factory,
):
    """Given a Subarray after the five point Calibration scan."""
    csp_sim = simulator_factory.get_or_create_simulator_device(
        SimulatorDeviceType.MID_CSP_DEVICE
    )
    sdp_sim = simulator_factory.get_or_create_simulator_device(
        SimulatorDeviceType.MID_SDP_DEVICE
    )

    event_recorder.subscribe_event(csp_sim, "obsState")
    event_recorder.subscribe_event(sdp_sim, "obsState")
    event_recorder.subscribe_event(subarray_node.subarray_node, "obsState")
    event_recorder.subscribe_event(
        subarray_node.subarray_node, "longRunningCommandResult"
    )
    event_recorder.subscribe_event(
        central_node_mid.central_node, "longRunningCommandResult"
    )

    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_mid", command_input_factory
    )
    _, unique_id = central_node_mid.store_resources(assign_input_json)
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.IDLE,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "longRunningCommandResult",
        (unique_id[0], str(int(ResultCode.OK))),
        lookahead=5,
    )
    subarray_node.simulate_receive_addresses_event(
        sdp_sim, command_input_factory
    )

    config_input_json = prepare_json_args_for_commands(
        "configure_mid", command_input_factory
    )
    subarray_node.execute_transition("Configure", config_input_json)

    for dish_master in subarray_node.dish_master_list:
        event_recorder.subscribe_event(dish_master, "dishMode")
        event_recorder.subscribe_event(dish_master, "pointingState")
        # Once Event recorder issue is fixed then use event
        # for assertion
        assert wait_and_validate_device_attribute_value(
            dish_master, "dishMode", DishMode.OPERATE, timeout=50
        )
        assert wait_and_validate_device_attribute_value(
            dish_master, "pointingState", PointingState.TRACK, timeout=50
        )
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
    assert check_subarray_obs_state("READY", 500, subarray_node=subarray_node)

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
    # Setting pointing calibration data
    subarray_node.set_pointing_cal_on_queue_connector()


@then(
    "the dish leaf node receive calibration solutions from SDP and "
    + "applies them to the Dishes"
)
def subarray_applies_calibration_solutions_to_dishes(
    subarray_node, event_recorder
):
    """Then the Subarray fetches and applies the configuration solutions to the
    dishes."""

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
def subarray_is_in_ready_obsstate(subarray_node):
    """Subarray is in READY obsState."""
    assert check_subarray_obs_state("READY", 500, subarray_node=subarray_node)
