"""Test module for long sequence functionality"""

import ast
import json
import logging

import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_ser_logging import configure_logging
from ska_tango_base.control_model import ObsState

from tests.resources.test_harness.central_node_mid import CentralNodeWrapperMid
from tests.resources.test_harness.event_recorder import EventRecorder
from tests.resources.test_harness.helpers import (
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
)
from tests.resources.test_harness.subarray_node import SubarrayNodeWrapper
from tests.resources.test_harness.utils.common_utils import JsonFactory
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
def check_telescope_in_initial_state(
    central_node_mid: CentralNodeWrapperMid, event_recorder: EventRecorder
):
    """
    Given a TMC
    """
    event_recorder.subscribe_event(
        central_node_mid.central_node, "telescopeState"
    )
    for dish_id in ["SKA001", "SKA036", "SKA063", "SKA100"]:
        event_recorder.subscribe_event(
            central_node_mid.dish_master_dict[dish_id], "dishMode"
        )

        assert event_recorder.has_change_event_occurred(
            central_node_mid.dish_master_dict[dish_id],
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
    subarray_node: SubarrayNodeWrapper,
    central_node_mid: CentralNodeWrapperMid,
    event_recorder: EventRecorder,
    command_input_factory: JsonFactory,
    resources: list,
    subarray_id: str,
):
    """
    Method to move subarray in IDLE obsState
    """
    event_recorder.subscribe_event(subarray_node.subarray_node, "obsState")
    event_recorder.subscribe_event(
        subarray_node.subarray_node, "assignedResources"
    )
    central_node_mid.set_subarray_id(subarray_id)

    central_node_mid.move_to_on()
    for dish_id in ["SKA001", "SKA036", "SKA063", "SKA100"]:
        event_recorder.subscribe_event(
            central_node_mid.dish_master_dict[dish_id], "dishMode"
        )

        assert event_recorder.has_change_event_occurred(
            central_node_mid.dish_master_dict[dish_id],
            "dishMode",
            DishMode.STANDBY_FP,
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
    subarray_node: SubarrayNodeWrapper,
    central_node_mid: CentralNodeWrapperMid,
    event_recorder: EventRecorder,
    command_input_factory: JsonFactory,
    subarray_id: str,
):
    """
    A method to invoke first Configure command
    """
    input_json = prepare_json_args_for_commands(
        "configure_mid", command_input_factory
    )
    configure_input_json = json.loads(input_json)
    configure_input_json["dish"]["receiver_band"] = "1"
    central_node_mid.set_subarray_id(subarray_id)
    subarray_node.execute_transition(
        "Configure", json.dumps(configure_input_json)
    )
    for dish_id in ["SKA001", "SKA036", "SKA063", "SKA100"]:
        event_recorder.subscribe_event(
            central_node_mid.dish_master_dict[dish_id], "pointingState"
        )
        event_recorder.subscribe_event(
            central_node_mid.dish_master_dict[dish_id], "dishMode"
        )

        assert event_recorder.has_change_event_occurred(
            central_node_mid.dish_master_dict[dish_id],
            "dishMode",
            DishMode.OPERATE,
        )

        assert event_recorder.has_change_event_occurred(
            central_node_mid.dish_master_dict[dish_id],
            "pointingState",
            PointingState.TRACK,
        )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.CONFIGURING,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.READY,
    )


@when(parsers.parse("I issue End command to the subarray {subarray_id}"))
def end_configuration_on_subarray(
    subarray_node: SubarrayNodeWrapper,
    central_node_mid: CentralNodeWrapperMid,
    event_recorder: EventRecorder,
    subarray_id: str,
):
    """
    A method to invoke end command
    """
    central_node_mid.set_subarray_id(subarray_id)
    subarray_node.execute_transition("End")
    for dish_id in ["SKA001", "SKA036", "SKA063", "SKA100"]:
        event_recorder.subscribe_event(
            central_node_mid.dish_master_dict[dish_id], "dishMode"
        )

        assert event_recorder.has_change_event_occurred(
            central_node_mid.dish_master_dict[dish_id],
            "dishMode",
            DishMode.STANDBY_FP,
        )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.IDLE,
    )


@when(
    parsers.parse("I reconfigure subarray {subarray_id} with receiver_band 2")
)
def reconfigure_subarray(
    subarray_node: SubarrayNodeWrapper,
    central_node_mid: CentralNodeWrapperMid,
    event_recorder: EventRecorder,
    command_input_factory: JsonFactory,
    subarray_id: str,
):
    """
    A method to invoke second Configure command
    """
    input_json = prepare_json_args_for_commands(
        "configure_mid", command_input_factory
    )
    configure_input_json = json.loads(input_json)
    configure_input_json["dish"]["receiver_band"] = "2"
    central_node_mid.set_subarray_id(subarray_id)
    subarray_node.execute_transition(
        "Configure", json.dumps(configure_input_json)
    )
    for dish_id in ["SKA001", "SKA036", "SKA063", "SKA100"]:
        event_recorder.subscribe_event(
            central_node_mid.dish_master_dict[dish_id], "pointingState"
        )
        event_recorder.subscribe_event(
            central_node_mid.dish_master_dict[dish_id], "dishMode"
        )

        assert event_recorder.has_change_event_occurred(
            central_node_mid.dish_master_dict[dish_id],
            "dishMode",
            DishMode.OPERATE,
            lookahead=16,
        )

        assert event_recorder.has_change_event_occurred(
            central_node_mid.dish_master_dict[dish_id],
            "pointingState",
            PointingState.TRACK,
        )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.CONFIGURING,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.READY,
    )


@when(parsers.parse("I issue scan command with {scan_id} on subarray"))
def invoke_scan(
    central_node_mid: CentralNodeWrapperMid,
    subarray_node: SubarrayNodeWrapper,
    command_input_factory: JsonFactory,
    event_recorder: EventRecorder,
    scan_id: str,
):
    """
    A method to invoke Scan command
    """
    scan_input_json = prepare_json_args_for_commands(
        "scan_mid", command_input_factory
    )
    subarray_node.execute_transition("Scan", scan_input_json)

    for dish_id in ["SKA001", "SKA036", "SKA063", "SKA100"]:
        event_recorder.subscribe_event(
            central_node_mid.dish_master_dict[dish_id], "scanID"
        )
        event_recorder.subscribe_event(
            central_node_mid.dish_master_dict[dish_id], "pointingState"
        )
        event_recorder.subscribe_event(
            central_node_mid.dish_master_dict[dish_id], "dishMode"
        )
        assert event_recorder.has_change_event_occurred(
            central_node_mid.dish_master_dict[dish_id],
            "scanID",
            scan_id,
        )

        assert (
            central_node_mid.dish_master_dict[dish_id].dishMode
            == DishMode.OPERATE
        )

        assert (
            central_node_mid.dish_master_dict[dish_id].pointingState
            == PointingState.TRACK
        )


@then("tmc subarraynode reports SCANNING obsState")
def check_tmc_subarray_scanning(
    subarray_node: SubarrayNodeWrapper,
    event_recorder: EventRecorder,
):
    """Checks if SubarrayNode's obsState attribute value is SCANNING"""
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.SCANNING,
    )
