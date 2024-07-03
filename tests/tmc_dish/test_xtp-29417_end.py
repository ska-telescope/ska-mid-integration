"""Test module for TMC-DISH End functionality"""


import logging

import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_tango_base.control_model import ObsState
from tango import DevState

from tests.conftest import wait_for_pointing_state_change
from tests.resources.test_harness.helpers import (
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
)

# from tests.resources.test_harness.utils.enums import SimulatorDeviceType
from tests.resources.test_support.common_utils.result_code import ResultCode
from tests.resources.test_support.enum import DishMode, PointingState


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
def given_a_telescope(central_node_mid, event_recorder, dish_ids):
    """
    Given a TMC
    """
    # csp_master_sim = simulator_factory.get_or_create_simulator_device(
    #     SimulatorDeviceType.MID_CSP_MASTER_DEVICE
    # )
    # sdp_master_sim = simulator_factory.get_or_create_simulator_device(
    #     SimulatorDeviceType.MID_SDP_MASTER_DEVICE
    # )

    assert central_node_mid.csp_master.ping() > 0
    assert central_node_mid.sdp_master.ping() > 0
    for dish_id in dish_ids.split(","):
        assert central_node_mid.dish_master_dict[dish_id].ping() > 0
        assert central_node_mid.dish_leaf_node_dict[dish_id].ping() > 0


@given("the Telescope is in ON state")
def turn_on_telescope(central_node_mid, event_recorder):
    """A method to put Telescope ON"""
    for dish_id in ["SKA001", "SKA036", "SKA063", "SKA100"]:
        event_recorder.subscribe_event(
            central_node_mid.dish_master_dict[dish_id], "dishMode"
        )
        event_recorder.subscribe_event(
            central_node_mid.dish_leaf_node_dict[dish_id], "dishMode"
        )
        event_recorder.subscribe_event(
            central_node_mid.dish_leaf_node_dict[dish_id], "pointingState"
        )
        event_recorder.subscribe_event(
            central_node_mid.dish_master_dict[dish_id], "pointingState"
        )

    # csp_master_sim = simulator_factory.get_or_create_simulator_device(
    #     SimulatorDeviceType.MID_CSP_MASTER_DEVICE
    # )
    # sdp_master_sim = simulator_factory.get_or_create_simulator_device(
    #     SimulatorDeviceType.MID_SDP_MASTER_DEVICE
    # )

    event_recorder.subscribe_event(
        central_node_mid.central_node, "telescopeState"
    )

    event_recorder.subscribe_event(central_node_mid.csp_master, "State")
    event_recorder.subscribe_event(central_node_mid.sdp_master, "State")

    central_node_mid.move_to_on()

    assert event_recorder.has_change_event_occurred(
        central_node_mid.csp_master,
        "State",
        DevState.ON,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.sdp_master,
        "State",
        DevState.ON,
    )

    for dish_id in ["SKA001", "SKA036", "SKA063", "SKA100"]:
        assert event_recorder.has_change_event_occurred(
            central_node_mid.dish_master_dict[dish_id],
            "dishMode",
            DishMode.STANDBY_FP,
        )
        assert event_recorder.has_change_event_occurred(
            central_node_mid.dish_leaf_node_dict[dish_id],
            "dishMode",
            DishMode.STANDBY_FP,
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
    event_recorder.subscribe_event(
        subarray_node.subarray_node, "longRunningCommandResult"
    )

    configure_input_json = prepare_json_args_for_commands(
        "configure_mid", command_input_factory
    )
    pytest.command_result = subarray_node.execute_transition(
        "Configure", configure_input_json
    )

    for dish_id in ["SKA001", "SKA036", "SKA063", "SKA100"]:
        assert event_recorder.has_change_event_occurred(
            central_node_mid.dish_master_dict[dish_id],
            "dishMode",
            DishMode.OPERATE,
            lookahead=10,
        )
        assert event_recorder.has_change_event_occurred(
            central_node_mid.dish_leaf_node_dict[dish_id],
            "dishMode",
            DishMode.OPERATE,
            lookahead=10,
        )
        assert event_recorder.has_change_event_occurred(
            central_node_mid.dish_master_dict[dish_id],
            "pointingState",
            PointingState.TRACK,
            lookahead=10,
        )
        assert event_recorder.has_change_event_occurred(
            central_node_mid.dish_leaf_node_dict[dish_id],
            "pointingState",
            PointingState.TRACK,
            lookahead=10,
        )
        logging.info(
            "DISHMODE for Dish %s: %s",
            dish_id,
            central_node_mid.dish_master_dict[dish_id].dishMode,
        )
        logging.info(
            "DISHMODE for DishLN %s: %s",
            dish_id,
            central_node_mid.dish_leaf_node_dict[dish_id].dishMode,
        )
        logging.info(
            "pointingState for Dish %s: %s",
            dish_id,
            central_node_mid.dish_master_dict[dish_id].pointingState,
        )
        logging.info(
            "pointingState for DishLN %s: %s",
            dish_id,
            central_node_mid.dish_leaf_node_dict[dish_id].pointingState,
        )

    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node, "obsState", ObsState.READY, lookahead=10
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "longRunningCommandResult",
        (pytest.command_result[1][0], str(ResultCode.OK.value)),
    )


@when(
    parsers.parse("I issue the End command to the TMC subarray {subarray_id}")
)
def invoke_end(central_node_mid, subarray_node, subarray_id, event_recorder):
    """A method to invoke End command"""
    central_node_mid.set_subarray_id(subarray_id)
    event_recorder.subscribe_event(
        subarray_node.subarray_node, "longRunningCommandResult"
    )
    pytest.command_result = subarray_node.execute_transition("End")


@then(
    parsers.parse("the DishMaster {dish_ids} transitions pointingState READY")
)
def check_dish_mode_and_pointing_state(
    central_node_mid, event_recorder, dish_ids
):
    """
    Method to check dishMode and pointingState of DISH
    """
    for dish_id in dish_ids.split(","):
        assert wait_for_pointing_state_change(
            PointingState.READY, central_node_mid.dish_master_dict[dish_id], 20
        )

        # assert event_recorder.has_change_event_occurred(
        #     central_node_mid.dish_master_dict[dish_id],
        #     "pointingState",
        #     PointingState.READY,
        #     lookahead=10,
        # )
        assert wait_for_pointing_state_change(
            PointingState.READY,
            central_node_mid.dish_leaf_node_dict[dish_id],
            20,
        )
        # assert event_recorder.has_change_event_occurred(
        #     central_node_mid.dish_leaf_node_dict[dish_id],
        #     "pointingState",
        #     PointingState.READY,
        #     lookahead=10,
        # )
        logging.info(
            "DISHMODE for Dish %s: %s",
            dish_id,
            central_node_mid.dish_master_dict[dish_id].dishMode,
        )
        logging.info(
            "DISHMODE for DishLN %s: %s",
            dish_id,
            central_node_mid.dish_leaf_node_dict[dish_id].dishMode,
        )
        logging.info(
            "pointingState for Dish %s: %s",
            dish_id,
            central_node_mid.dish_master_dict[dish_id].pointingState,
        )
        logging.info(
            "pointingState for DishLN %s: %s",
            dish_id,
            central_node_mid.dish_leaf_node_dict[dish_id].pointingState,
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
        subarray_node.subarray_node, "obsState", ObsState.IDLE, lookahead=10
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "longRunningCommandResult",
        (pytest.command_result[1][0], str(ResultCode.OK.value)),
    )
