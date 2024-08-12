"""Test module for TMC-DISH Configure functionality with correction
key handling.
"""
import json

import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_tango_base.control_model import ObsState
from tango import DeviceProxy, DevState

from tests.resources.test_harness.constant import COMMAND_COMPLETED
from tests.resources.test_harness.helpers import (
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
)
from tests.resources.test_harness.utils.enums import SimulatorDeviceType
from tests.resources.test_support.enum import DishMode, PointingState

POINTING_CAL = [1.1, 1.1, 1.2]


@pytest.mark.SKA_mid
@scenario(
    "../features/tmc_dish/xtp-29416_configure_with_correction_key.feature",
    "Configure the telescope having TMC and Dish Subsystems with "
    + "correction key",
)
def test_tmc_dish_configure_with_correction_key():
    """
    Test case to verify TMC-DISH Configure functionality with
    correction key handling
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


@given("the TMC subarray is in IDLE obsState")
def subarray_is_in_idle_obsState(
    central_node_mid,
    subarray_node,
    event_recorder,
    command_input_factory,
    simulator_factory,
):
    # Setup and verification steps to ensure the subarray is in IDLE obsState
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
        (unique_id[0], COMMAND_COMPLETED),
        lookahead=5,
    )
    subarray_node.simulate_receive_addresses_event(
        sdp_sim, command_input_factory
    )


@when(
    parsers.parse(
        "I issue the Configure command to the TMC subarray {subarray_id} with "
        + "correction key {correction_key}"
    )
)
def invoke_configure_with_correction_key(
    subarray_node,
    command_input_factory,
    correction_key,
):
    """
    A method to invoke Configure command with a correction key

    Args:
        central_node_mid: Fixture for a TMC CentralNode wrapper class
        subarray_node: Fixture for a Subarray Node wrapper class
        command_input_factory: fixture for creating input required for command
        subarray_id (str): Subarray ID
        correction_key (str): Correction key (UPDATE, RESET, MAINTAIN, or
        blank)
        event_recorder: Fixture for EventRecorder class
    """

    config_input_json = prepare_json_args_for_commands(
        "configure_mid", command_input_factory
    )
    # Update the configuration with the correction key
    configure_data = json.loads(config_input_json)
    configure_data["pointing"]["correction"] = correction_key
    configure_input_str = json.dumps(configure_data)

    # Set offsets on the SDP queue connector
    queue_connector = DeviceProxy("mid-sdp/queueconnector/01")
    queue_connector.SetPointingCalSka001(POINTING_CAL)
    subarray_node.execute_transition("Configure", configure_input_str)


@then(
    parsers.parse(
        "the DishMaster transitions to dishMode OPERATE and pointingState "
        + "TRACK"
    )
)
def check_dish_mode_and_pointing_state(central_node_mid, event_recorder):
    """
    Method to check dishMode and pointingState of DISH

    Args:
        central_node_mid: Fixture for a TMC CentralNode wrapper class
        event_recorder: Fixture for EventRecorder class
    """
    for dish_master in central_node_mid.dish_master_dict.values():
        event_recorder.subscribe_event(dish_master, "pointingState")
        assert event_recorder.has_change_event_occurred(
            dish_master,
            "dishMode",
            DishMode.OPERATE,
            lookahead=10,
        )
        assert event_recorder.has_change_event_occurred(
            dish_master,
            "pointingState",
            PointingState.TRACK,
            lookahead=10,
        )


@then(
    parsers.parse(
        "TMC subarray {subarray_id} obsState transitions to READY obsState"
    )
)
def check_subarray_obsState_ready(
    central_node_mid, subarray_node, event_recorder, subarray_id
):
    """
    Method to check subarray is in READY obsState

    Args:
        central_node_mid: Fixture for a TMC CentralNode wrapper class
        subarray_node: Fixture for a Subarray Node wrapper class
        event_recorder: Fixture for EventRecorder class
        subarray_id (str): Subarray ID
    """
    central_node_mid.set_subarray_id(subarray_id)
    event_recorder.subscribe_event(
        subarray_node.subarray_devices["sdp_subarray"], "obsState"
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_devices["sdp_subarray"],
        "obsState",
        ObsState.READY,
        lookahead=10,
    )
    event_recorder.subscribe_event(
        subarray_node.subarray_devices["csp_subarray"], "obsState"
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_devices["csp_subarray"],
        "obsState",
        ObsState.READY,
        lookahead=10,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node, "obsState", ObsState.READY, lookahead=10
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "longRunningCommandResult",
        (pytest.command_result[1][0], COMMAND_COMPLETED),
    )
