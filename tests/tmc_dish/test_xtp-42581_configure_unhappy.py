"""Test module for TMC-DISH Configure functionality"""

import json
import time

import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_tango_base.control_model import ObsState
from ska_tango_testing.mock.placeholders import Anything
from tango import DevState

from tests.resources.test_harness.helpers import (
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
)
from tests.resources.test_support.common_utils.result_code import ResultCode
from tests.resources.test_support.enum import DishMode, PointingState


@pytest.mark.tmc_dish
@scenario(
    "../features/tmc_dish/xtp-42581_configure_unhappy.feature",
    "Testing of successive configure functionality with same receiver_band",
)
def test_tmc_dish_successive_configure_with_same_receiver_band():
    """
    Test case to verify TMC-DISH successive Configure functionality
    with same receiver band.

    Glossary:
        - "central_node_mid": fixture for a TMC CentralNode under test
        - "simulator_factory": fixture for SimulatorFactory class,
        which provides simulated master devices
        - "event_recorder": fixture for EventRecorder class
    """


@given("a Telescope in ON state")
def turn_on_telescope(central_node_mid, event_recorder):
    """
    A method to put Telescope ON
    """
    event_recorder.subscribe_event(
        central_node_mid.central_node, "telescopeState"
    )
    for dish_id in ["SKA001", "SKA036", "SKA063", "SKA100"]:
        event_recorder.subscribe_event(
            central_node_mid.dish_master_dict[dish_id], "dishMode", 500.0
        )
        event_recorder.subscribe_event(
            central_node_mid.dish_master_dict[dish_id], "pointingState", 500.0
        )

    # TODO: Improvement in tests/implementation
    # to minimize the need of having sleep

    time.sleep(5)
    central_node_mid.move_to_on()

    for dish_id in ["SKA001", "SKA036", "SKA063", "SKA100"]:
        assert event_recorder.has_change_event_occurred(
            central_node_mid.dish_master_dict[dish_id],
            "dishMode",
            DishMode.STANDBY_FP,
        )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "telescopeState",
        DevState.ON,
    )


@given("the subarray is in IDLE obsState")
def check_subarray_obsState_idle(
    subarray_node, central_node_mid, event_recorder, command_input_factory
):
    """
    Method to check subarray is in IDLE obsState
    """
    event_recorder.subscribe_event(
        subarray_node.subarray_node, "obsState", 500
    )

    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_mid", command_input_factory
    )

    pytest.command_result = central_node_mid.store_resources(assign_input_json)

    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.IDLE,
    )
    event_recorder.subscribe_event(
        central_node_mid.central_node, "longRunningCommandResult"
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "longRunningCommandResult",
        (pytest.command_result[1][0], str(ResultCode.OK.value)),
    )


@given(
    parsers.parse(
        "the command configure is issued to the TMC subarray "
        + "with {receiver_band}"
    )
)
def invoke_configure(
    subarray_node, command_input_factory, receiver_band, event_recorder
):
    """
    A method to invoke Configure command
    """
    event_recorder.subscribe_event(
        subarray_node.subarray_node, "longRunningCommandResult"
    )
    configure_input_json = prepare_json_args_for_commands(
        "configure_mid", command_input_factory
    )
    configure_input = json.loads(configure_input_json)
    configure_input["dish"]["receiver_band"] = receiver_band
    pytest.command_result = subarray_node.store_configuration_data(
        json.dumps(configure_input)
    )


@given("the subarray transitions to obsState READY")
def check_dish_mode_and_pointing_state(
    subarray_node, event_recorder, central_node_mid
):
    """
    Method to check dishMode and pointingState of DISH and
    SubarrayNode obsState.
    """
    for dish_id in ["SKA001", "SKA036", "SKA063", "SKA100"]:
        event_recorder.subscribe_event(
            central_node_mid.dish_master_dict[dish_id], "dishMode", 500.0
        )
        event_recorder.subscribe_event(
            central_node_mid.dish_master_dict[dish_id], "pointingState", 500.0
        )
        assert event_recorder.has_change_event_occurred(
            central_node_mid.dish_master_dict[dish_id],
            "dishMode",
            DishMode.OPERATE,
            lookahead=15,
        )

        assert event_recorder.has_change_event_occurred(
            central_node_mid.dish_master_dict[dish_id],
            "pointingState",
            PointingState.TRACK,
            lookahead=15,
        )
    time.sleep(5)
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.READY,
        lookahead=15,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "longRunningCommandResult",
        (pytest.command_result[1][0], str(ResultCode.OK.value)),
    )


@when(
    parsers.parse(
        "the next successive configure command is issued to the TMC "
        + "subarray with {receiver_band}"
    )
)
def invoke_successive_configure(
    subarray_node,
    command_input_factory,
    receiver_band,
    event_recorder,
    central_node_mid,
):
    """
    A method to invoke Configure command
    """
    for dish_id in ["SKA001", "SKA036", "SKA063", "SKA100"]:
        event_recorder.subscribe_event(
            central_node_mid.dish_master_dict[dish_id],
            "longRunningCommandStatus",
        )

    configure_input_json = prepare_json_args_for_commands(
        "configure_mid", command_input_factory
    )
    configure_input = json.loads(configure_input_json)
    configure_input["dish"]["receiver_band"] = receiver_band
    subarray_node.execute_transition("Configure", json.dumps(configure_input))


@then(
    parsers.parse(
        "the dish rejects the command with message receiver band is "
        + "already band B{receiver_band}"
    )
)
def configure_command_rejection_by_dish(
    receiver_band, event_recorder, central_node_mid
):
    # In order to complete this clause, error propagation for TMC-Dish
    # interface needs to be completed.
    for dish_id in ["SKA001", "SKA036", "SKA063", "SKA100"]:
        assert event_recorder.has_change_event_occurred(
            central_node_mid.dish_master_dict[dish_id],
            "longRunningCommandStatus",
            (Anything, "REJECTED"),
            lookahead=5,
        )


@then("TMC subarray remains in obsState READY")
def check_dish_mode_and_pointing_state_again(subarray_node, event_recorder):
    """
    Method to check SubarrayNode obsState.
    """
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node, "obsState", ObsState.READY, lookahead=10
    )
