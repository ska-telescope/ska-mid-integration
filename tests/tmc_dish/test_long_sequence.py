"""Test module for long sequence functionality"""

import ast
import logging

import pytest
from pytest_bdd import given, parsers, scenario, when
from ska_ser_logging import configure_logging
from ska_tango_base.control_model import ObsState

from tests.resources.test_harness.helpers import (
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
)
from tests.resources.test_support.enum import DishMode, PointingState

# import time

# from tango import DevState


configure_logging(logging.DEBUG)
LOGGER = logging.getLogger(__name__)


@pytest.mark.tmc_dish
@scenario(
    "../features/tmc_dish/long_sequence.feature",
    "TMC executes long sequence of commands successfully",
)
def test_tmc_dish_long_sequence_functionality():
    """
    Test case to verify TMC-DISH long sequence functionality
    """


@given("a telescope in OFF or STANDBY state")
def check_telescope_in_initial_state(central_node_mid, event_recorder):
    """
    Given a TMC
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
    event_recorder.subscribe_event(
        central_node_mid.central_node, "telescopeState"
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
    # Wait for DishMaster attribute value update,
    # on CentralNode for value dishMode STANDBY_FP

    # TODO: Improvement in tests/implementation
    # to minimize the need of having sleep
    # time.sleep(50)
    # Resource(central_node_mid.central_node).assert_attribute(
    #     "telescopeState"
    # ).equals(["OFF", "STANDBY"])
    # assert event_recorder.has_change_event_occurred(
    #     central_node_mid.central_node,
    #     "telescopeState",
    #     DevState.OFF,
    #     lookahead=30,
    # )


@when(parsers.parse("I assign {resources} to TMC subarray {subarray_id}"))
def move_subarray_to_obsState_idle(
    subarray_node,
    central_node_mid,
    event_recorder,
    command_input_factory,
    resources,
    subarray_id,
):
    """
    Method to check subarray is in IDLE obsState
    """
    event_recorder.subscribe_event(subarray_node.subarray_node, "obsState")
    event_recorder.subscribe_event(
        subarray_node.subarray_node, "assignedResources"
    )
    central_node_mid.set_subarray_id(subarray_id)
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_mid", command_input_factory
    )

    central_node_mid.store_resources(assign_input_json)

    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.IDLE,
    )
    LOGGER.info(
        f"Assigned Resources: {subarray_node.subarray_node.assignedResources}"
    )
    LOGGER.info(f"Resources:{resources}")
    LOGGER.info(f"Resources convert:{ast.literal_eval(resources)}")
    # assert event_recorder.has_change_event_occurred(
    #     subarray_node.subarray_node,
    #     "assignedResources",
    #     ast.literal_eval(resources),  # casts string coded tuple to tuple
    # )


@when(
    parsers.parse(
        "I configure the subarray {subarray_id} with receiver_band_1"
    )
)
def configure_subarray(
    subarray_node,
    central_node_mid,
    event_recorder,
    command_input_factory,
    subarray_id,
):
    """
    A method to invoke Configure command
    """
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
    event_recorder.subscribe_event(
        central_node_mid.central_node, "telescopeState"
    )
    configure_input_json = prepare_json_args_for_commands(
        "configure_mid", command_input_factory
    )
    central_node_mid.set_subarray_id(subarray_id)
    subarray_node.execute_transition("Configure", configure_input_json)
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
    # for dish_id in [SKA001, SKA036, SKA063, "SKA100"]:
    #     event_recorder.subscribe_event(
    #         central_node_mid.dish_master_dict[dish_id], "pointingState"
    #     )
    #     event_recorder.subscribe_event(
    #         central_node_mid.dish_master_dict[dish_id], "dishMode"
    #     )

    #     assert event_recorder.has_change_event_occurred(
    #         central_node_mid.dish_master_dict[dish_id],
    #         "dishMode",
    #         DishMode.OPERATE,
    #         lookahead=15,
    #     )

    #     assert event_recorder.has_change_event_occurred(
    #         central_node_mid.dish_master_dict[dish_id],
    #         "pointingState",
    #         PointingState.TRACK,
    #         lookahead=15,
    #     )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.READY,
    )


@when(parsers.parse("I issue End command to the subarray {subarray_id}"))
def end_configuration_on_subarray(
    subarray_node,
    central_node_mid,
    event_recorder,
    subarray_id,
):
    """
    A method to invoke end command
    """
    central_node_mid.set_subarray_id(subarray_id)
    subarray_node.execute_transition("End")
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
        ObsState.IDLE,
    )
