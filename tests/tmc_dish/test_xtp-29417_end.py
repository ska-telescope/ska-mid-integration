"""Test module for TMC-DISH End functionality"""

import time

import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_tango_base.control_model import ObsState
from tango import DevState

from tests.resources.test_harness.helpers import (
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
)
from tests.resources.test_harness.utils.enums import SimulatorDeviceType
from tests.resources.test_support.enum import DishMode, PointingState


# @pytest.mark.xfail(reason="Enable when SKB-292, SKB-293 are resolved")
@pytest.mark.tmc_dish
@scenario(
    "../features/tmc_dish/xtp-29417_end.feature",
    "TMC executes End command on DISH.LMC",
)
def test_tmc_dish_end():
    """
    Test case to verify TMC-DISH End functionality

    Glossary:
        - "central_node_mid": fixture for a TMC CentralNode under test
        - "simulator_factory": fixture for SimulatorFactory class,
        which provides simulated master devices
        - "event_recorder": fixture for EventRecorder class
    """


@given(
    parsers.parse(
        "a Telescope consisting of TMC, DISH {dish_ids},"
        + " simulated CSP and simulated SDP"
    )
)
def given_a_telescope(
    central_node_mid, simulator_factory, event_recorder, dish_ids
):
    """
    Given a TMC
    """
    csp_master_sim = simulator_factory.get_or_create_simulator_device(
        SimulatorDeviceType.MID_CSP_MASTER_DEVICE
    )
    sdp_master_sim = simulator_factory.get_or_create_simulator_device(
        SimulatorDeviceType.MID_SDP_MASTER_DEVICE
    )

    assert csp_master_sim.ping() > 0
    assert sdp_master_sim.ping() > 0
    for dish_id in dish_ids.split(","):
        assert central_node_mid.dish_master_dict[dish_id].ping() > 0


@given("the Telescope is in ON state")
def turn_on_telescope(central_node_mid, event_recorder, simulator_factory):
    """A method to put Telescope ON"""
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

    assert event_recorder.has_change_event_occurred(
        central_node_mid.dish_master_dict["SKA001"],
        "dishMode",
        DishMode.STANDBY_LP,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.dish_master_dict["SKA036"],
        "dishMode",
        DishMode.STANDBY_LP,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.dish_master_dict["SKA063"],
        "dishMode",
        DishMode.STANDBY_LP,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.dish_master_dict["SKA100"],
        "dishMode",
        DishMode.STANDBY_LP,
    )

    # Wait for the DishLeafNode to get StandbyLP event form DishMaster before
    # invoking TelescopeOn command
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

    assert event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "telescopeState",
        DevState.OFF,
    )
    central_node_mid.move_to_on()

    assert event_recorder.has_change_event_occurred(
        central_node_mid.dish_master_dict["SKA001"],
        "dishMode",
        DishMode.STANDBY_FP,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.dish_master_dict["SKA036"],
        "dishMode",
        DishMode.STANDBY_FP,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.dish_master_dict["SKA063"],
        "dishMode",
        DishMode.STANDBY_FP,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.dish_master_dict["SKA100"],
        "dishMode",
        DishMode.STANDBY_FP,
    )

    # Wait for the DishLeafNode to get StandbyFP event form DishMaster before
    # invoking TelescopeOn command
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


@given(parsers.parse("TMC subarray {subarray_id} is in READY ObsState"))
def check_subarray_obsstate(
    subarray_node,
    command_input_factory,
    event_recorder,
    central_node_mid,
    subarray_id,
):
    """Method to check subarray is in READY obstate"""
    event_recorder.subscribe_event(subarray_node.subarray_node, "obsState")

    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_mid", command_input_factory
    )
    central_node_mid.set_subarray_id(subarray_id)
    central_node_mid.store_resources(assign_input_json)

    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.IDLE,
    )
    configure_input_json = prepare_json_args_for_commands(
        "configure_mid", command_input_factory
    )

    subarray_node.execute_transition("Configure", configure_input_json)

    assert event_recorder.has_change_event_occurred(
        central_node_mid.dish_master_dict["SKA001"],
        "dishMode",
        DishMode.OPERATE,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.dish_master_dict["SKA036"],
        "dishMode",
        DishMode.OPERATE,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.dish_master_dict["SKA063"],
        "dishMode",
        DishMode.OPERATE,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.dish_master_dict["SKA100"],
        "dishMode",
        DishMode.OPERATE,
    )

    event_recorder.subscribe_event(
        central_node_mid.dish_master_dict["SKA001"], "pointingState"
    )
    event_recorder.subscribe_event(
        central_node_mid.dish_master_dict["SKA036"], "pointingState"
    )
    event_recorder.subscribe_event(
        central_node_mid.dish_master_dict["SKA063"], "pointingState"
    )
    event_recorder.subscribe_event(
        central_node_mid.dish_master_dict["SKA100"], "pointingState"
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.dish_master_dict["SKA001"],
        "pointingState",
        PointingState.TRACK,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.dish_master_dict["SKA036"],
        "pointingState",
        PointingState.TRACK,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.dish_master_dict["SKA063"],
        "pointingState",
        PointingState.TRACK,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.dish_master_dict["SKA100"],
        "pointingState",
        PointingState.TRACK,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.READY,
    )


@when(
    parsers.parse("I issue the End command to the TMC subarray {subarray_id}")
)
def invoke_end(central_node_mid, subarray_node, subarray_id):
    """A method to invoke End command"""
    central_node_mid.set_subarray_id(subarray_id)
    subarray_node.execute_transition("End")


@then(
    parsers.parse(
        "the DishMaster {dish_ids} transitions to dishMode"
        + " OPERATE and pointingState READY"
    )
)
def check_dish_mode_and_pointing_state(
    central_node_mid, event_recorder, dish_ids
):
    """
    Method to check dishMode and pointingState of DISH
    """
    for dish_id in dish_ids.split(","):
        assert event_recorder.has_change_event_occurred(
            central_node_mid.dish_master_dict[dish_id],
            "dishMode",
            DishMode.OPERATE,
        )

        assert event_recorder.has_change_event_occurred(
            central_node_mid.dish_master_dict[dish_id],
            "pointingState",
            PointingState.READY,
        )


@then(
    parsers.parse(
        "TMC subarray {subarray_id} obsState transitions to IDLE obsState"
    )
)
def check_subarray_obsState_idle(
    central_node_mid, subarray_node, event_recorder, subarray_id
):
    """Method to check subarray is in IDLE obstate"""
    central_node_mid.set_subarray_id(subarray_id)
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.IDLE,
    )
