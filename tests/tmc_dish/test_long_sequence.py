"""Test module for TMC-DISH Configure functionality"""

import json
import time

import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_tango_base.control_model import ObsState
from tango import DevState

# from tests.conftest import LOGGER
from tests.resources.test_harness.helpers import (
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
)
from tests.resources.test_harness.utils.enums import SimulatorDeviceType
from tests.resources.test_support.enum import DishMode  # PointingState


@pytest.mark.tmc_dish
@scenario(
    "../features/tmc_dish/long_sequence.feature",
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
def turn_on_telescope(central_node_mid, event_recorder, simulator_factory):
    """
    A method to put Telescope ON
    """
    event_recorder.subscribe_event(
        central_node_mid.dish_master_dict["SKA001"], "dishMode"
    )
    event_recorder.subscribe_event(
        central_node_mid.dish_master_dict["SKA036"], "dishMode"
    )
    event_recorder.subscribe_event(
        central_node_mid.dish_master_dict["SKA063"], "dishMode"
    )
    event_recorder.subscribe_event(
        central_node_mid.dish_master_dict["SKA100"], "dishMode"
    )

    # TODO: Improvement in tests/implementation
    # to minimize the need of having sleep

    time.sleep(5)
    csp_master_sim = simulator_factory.get_or_create_simulator_device(
        SimulatorDeviceType.MID_CSP_MASTER_DEVICE
    )
    sdp_master_sim = simulator_factory.get_or_create_simulator_device(
        SimulatorDeviceType.MID_SDP_MASTER_DEVICE
    )

    event_recorder.subscribe_event(
        central_node_mid.central_node, "telescopeState"
    )

    event_recorder.subscribe_event(csp_master_sim, "State")
    event_recorder.subscribe_event(sdp_master_sim, "State")

    central_node_mid.move_to_on()

    assert event_recorder.has_change_event_occurred(
        central_node_mid.dish_master_dict["SKA001"],
        "dishMode",
        DishMode.STANDBY_FP,
        lookahead=15,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.dish_master_dict["SKA036"],
        "dishMode",
        DishMode.STANDBY_FP,
        lookahead=15,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.dish_master_dict["SKA063"],
        "dishMode",
        DishMode.STANDBY_FP,
        lookahead=15,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.dish_master_dict["SKA100"],
        "dishMode",
        DishMode.STANDBY_FP,
        lookahead=15,
    )

    # Wait for DishMaster attribute value update,
    # on CentralNode for value dishMode STANDBY_FP

    # TODO: Improvement in tests/implementation
    # to minimize the need of having sleep
    time.sleep(5)

    assert event_recorder.has_change_event_occurred(
        central_node_mid.sdp_master,
        "State",
        DevState.ON,
    )

    assert event_recorder.has_change_event_occurred(
        central_node_mid.csp_master,
        "State",
        DevState.ON,
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
    event_recorder.subscribe_event(subarray_node.subarray_node, "obsState")

    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_mid", command_input_factory
    )

    central_node_mid.store_resources(assign_input_json)

    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.IDLE,
    )


@given(
    parsers.parse(
        "the command configure is issued to the TMC subarray "
        + "with {receiver_band}"
    )
)
def invoke_configure(subarray_node, command_input_factory, receiver_band):
    """
    A method to invoke Configure command
    """
    configure_input_json = prepare_json_args_for_commands(
        "configure_mid", command_input_factory
    )
    configure_input = json.loads(configure_input_json)
    configure_input["dish"]["receiver_band"] = receiver_band
    subarray_node.execute_transition("Configure", json.dumps(configure_input))


@given("the subarray transitions to obsState READY")
def check_dish_mode_and_pointing_state(subarray_node, event_recorder):
    """
    Method to check dishMode and pointingState of DISH and
    SubarrayNode obsState.
    """
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.READY,
    )


@when(
    parsers.parse(
        "the next successive configure command is issued to the TMC "
        + "subarray with {receiver_band}"
    )
)
def invoke_successive_configure(
    subarray_node, command_input_factory, receiver_band
):
    """
    A method to invoke Configure command
    """
    configure_input_json = prepare_json_args_for_commands(
        "configure_mid", command_input_factory
    )
    configure_input = json.loads(configure_input_json)
    configure_input["dish"]["receiver_band"] = str(receiver_band)
    subarray_node.execute_transition("Configure", json.dumps(configure_input))


@then(
    parsers.parse(
        "the dish rejects the command with message receiver band is "
        + "already band B{receiver_band}"
    )
)
def command_rejection(receiver_band):
    pass


@then("TMC subarray remains in obsState READY")
def check_dish_mode_and_pointing_state_again(subarray_node):
    """
    Method to check SubarrayNode obsState.
    """
    subarray_obsstate = subarray_node.subarray_node.read_attribute(
        "obsState"
    ).val
    assert subarray_obsstate == ObsState.READY
