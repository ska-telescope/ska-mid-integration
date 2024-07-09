"""Test module for long sequence functionality"""

import json
import logging

import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_ser_logging import configure_logging
from ska_tango_base.control_model import ObsState
from tango import DevState

from tests.resources.test_harness.central_node_mid import CentralNodeWrapperMid
from tests.resources.test_harness.event_recorder import EventRecorder
from tests.resources.test_harness.helpers import (
    check_long_running_command_status,
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
)
from tests.resources.test_harness.subarray_node import SubarrayNodeWrapper
from tests.resources.test_harness.utils.common_utils import JsonFactory
from tests.resources.test_harness.utils.enums import SimulatorDeviceType

# from tests.resources.test_support.common_utils.common_helpers import Resource
from tests.resources.test_support.common_utils.result_code import ResultCode
from tests.resources.test_support.enum import DishMode, PointingState

configure_logging(logging.DEBUG)
LOGGER = logging.getLogger(__name__)


@pytest.mark.tmc_dish
@scenario(
    "../features/tmc_dish/xtp-42658_long_sequence.feature",
    "TMC executes long sequence of commands successfully",
)
def test_tmc_dish_long_sequence_functionality():
    """
    Test case to verify TMC-DISH long sequence functionality
    """


@given(
    parsers.parse(
        "a Telescope consisting of TMC, DISH {dish_ids},"
        + " simulated CSP and simulated SDP"
    )
)
def given_a_telescope(central_node_mid, simulator_factory, dish_ids):
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
        assert central_node_mid.dish_leaf_node_dict[dish_id].ping() > 0


@given("the Telescope is in ON state")
def turn_on_telescope(central_node_mid, event_recorder, simulator_factory):
    """
    A method to put Telescope ON
    """
    for dish_id in ["SKA001", "SKA036", "SKA063", "SKA100"]:
        event_recorder.subscribe_event(
            central_node_mid.dish_master_dict[dish_id], "dishMode"
        )
        event_recorder.subscribe_event(
            central_node_mid.dish_leaf_node_dict[dish_id], "dishMode"
        )

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


@when(parsers.parse("I assign {dish_ids} to TMC subarray {subarray_id}"))
def move_subarray_to_obsState_idle(
    subarray_node: SubarrayNodeWrapper,
    central_node_mid: CentralNodeWrapperMid,
    event_recorder: EventRecorder,
    command_input_factory: JsonFactory,
    dish_ids: list,
    subarray_id: str,
):
    """
    Method to move subarray in IDLE obsState
    """
    event_recorder.subscribe_event(subarray_node.subarray_node, "obsState")

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
    event_recorder.subscribe_event(
        subarray_node.subarray_node, "longRunningCommandResult"
    )
    input_json = prepare_json_args_for_commands(
        "configure_mid", command_input_factory
    )
    configure_input_json = json.loads(input_json)
    configure_input_json["dish"]["receiver_band"] = "1"
    configure_input_json["csp"]["common"]["frequency_band"] = "1"
    central_node_mid.set_subarray_id(subarray_id)
    pytest.command_result = subarray_node.store_configuration_data(
        json.dumps(configure_input_json)
    )
    for dish_id in ["SKA001", "SKA036", "SKA063", "SKA100"]:
        event_recorder.subscribe_event(
            central_node_mid.dish_master_dict[dish_id], "pointingState"
        )
        event_recorder.subscribe_event(
            central_node_mid.dish_leaf_node_dict[dish_id], "pointingState"
        )
        logging.info(
            "DISHMODE for Dish after configure 1 %s: %s",
            dish_id,
            central_node_mid.dish_master_dict[dish_id].dishMode,
        )
        logging.info(
            "DISHMODE for DishLN after configure 1 %s: %s",
            dish_id,
            central_node_mid.dish_leaf_node_dict[dish_id].dishMode,
        )
        logging.info(
            "pointingState for Dish after configure 1 %s: %s",
            dish_id,
            central_node_mid.dish_master_dict[dish_id].pointingState,
        )
        logging.info(
            "pointingState for DishLN after configure 1 %s: %s",
            dish_id,
            central_node_mid.dish_leaf_node_dict[dish_id].pointingState,
        )
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
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.READY,
        lookahead=10,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "longRunningCommandResult",
        (pytest.command_result[1][0], str(ResultCode.OK.value)),
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
    # pytest.command_result = subarray_node.end_observation()
    pytest.command_result = subarray_node.execute_transition("End")
    for dish_id in ["SKA001", "SKA036", "SKA063", "SKA100"]:
        logging.info(
            "DISHMODE for Dish after end %s: %s",
            dish_id,
            central_node_mid.dish_master_dict[dish_id].dishMode,
        )
        logging.info(
            "DISHMODE for DishLN after end %s: %s",
            dish_id,
            central_node_mid.dish_leaf_node_dict[dish_id].dishMode,
        )
        logging.info(
            "pointingState for Dish after end %s: %s",
            dish_id,
            central_node_mid.dish_master_dict[dish_id].pointingState,
        )
        logging.info(
            "pointingState for DishLN after end %s: %s",
            dish_id,
            central_node_mid.dish_leaf_node_dict[dish_id].pointingState,
        )
        # assert event_recorder.has_change_event_occurred(
        #     central_node_mid.dish_master_dict[dish_id],
        #     "dishMode",
        #     DishMode.STANDBY_FP,
        #     lookahead=10,
        # )
        # assert event_recorder.has_change_event_occurred(
        #     central_node_mid.dish_leaf_node_dict[dish_id],
        #     "dishMode",
        #     DishMode.STANDBY_FP,
        #     lookahead=10,
        # )
        assert event_recorder.has_change_event_occurred(
            central_node_mid.dish_master_dict[dish_id],
            "pointingState",
            PointingState.READY,
            lookahead=10,
        )
        assert event_recorder.has_change_event_occurred(
            central_node_mid.dish_leaf_node_dict[dish_id],
            "pointingState",
            PointingState.READY,
            lookahead=10,
        )

    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.IDLE,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "longRunningCommandResult",
        (pytest.command_result[1][0], str(ResultCode.OK.value)),
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
    event_recorder.subscribe_event(
        subarray_node.subarray_node, "longRunningCommandResult"
    )
    input_json = prepare_json_args_for_commands(
        "configure_mid", command_input_factory
    )
    configure_input_json = json.loads(input_json)
    configure_input_json["dish"]["receiver_band"] = "2"
    central_node_mid.set_subarray_id(subarray_id)
    pytest.command_result = subarray_node.store_configuration_data(
        json.dumps(configure_input_json)
    )

    for dish_id in ["SKA001", "SKA036", "SKA063", "SKA100"]:
        logging.info(
            "DISHMODE for Dish after configure 2 %s: %s",
            dish_id,
            central_node_mid.dish_master_dict[dish_id].dishMode,
        )
        logging.info(
            "DISHMODE for DishLN after configure 2 %s: %s",
            dish_id,
            central_node_mid.dish_leaf_node_dict[dish_id].dishMode,
        )
        logging.info(
            "pointingState for Dish after configure 2 %s: %s",
            dish_id,
            central_node_mid.dish_master_dict[dish_id].pointingState,
        )
        logging.info(
            "pointingState for DishLN after configure 2 %s: %s",
            dish_id,
            central_node_mid.dish_leaf_node_dict[dish_id].pointingState,
        )
        assert (
            central_node_mid.dish_master_dict[dish_id].dishMode
            == DishMode.OPERATE
        )
        assert (
            central_node_mid.dish_leaf_node_dict[dish_id].dishMode
            == DishMode.OPERATE
        )
        # assert event_recorder.has_change_event_occurred(
        #     central_node_mid.dish_master_dict[dish_id],
        #     "dishMode",
        #     DishMode.OPERATE,
        #     lookahead=10,
        # )
        # assert event_recorder.has_change_event_occurred(
        #     central_node_mid.dish_leaf_node_dict[dish_id],
        #     "dishMode",
        #     DishMode.OPERATE,
        #     lookahead=10,
        # )
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
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.READY,
        lookahead=10,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "longRunningCommandResult",
        (pytest.command_result[1][0], str(ResultCode.OK.value)),
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
    # subarray_node.store_scan_data(scan_input_json)
    pytest.command_result = subarray_node.execute_transition(
        "Scan", scan_input_json
    )

    for dish_id in ["SKA001", "SKA036", "SKA063", "SKA100"]:
        event_recorder.subscribe_event(
            central_node_mid.dish_master_dict[dish_id], "scanID"
        )
        assert event_recorder.has_change_event_occurred(
            central_node_mid.dish_master_dict[dish_id],
            "scanID",
            scan_id,
        )
        logging.info(
            "DISHMODE for Dish after scan %s: %s",
            dish_id,
            central_node_mid.dish_master_dict[dish_id].dishMode,
        )
        logging.info(
            "DISHMODE for DishLN after scan%s: %s",
            dish_id,
            central_node_mid.dish_leaf_node_dict[dish_id].dishMode,
        )
        logging.info(
            "pointingState for Dish after scan  %s: %s",
            dish_id,
            central_node_mid.dish_master_dict[dish_id].pointingState,
        )
        logging.info(
            "pointingState for DishLN after scan %s: %s",
            dish_id,
            central_node_mid.dish_leaf_node_dict[dish_id].pointingState,
        )
        assert (
            central_node_mid.dish_master_dict[dish_id].dishMode
            == DishMode.OPERATE
        )
        assert (
            central_node_mid.dish_leaf_node_dict[dish_id].dishMode
            == DishMode.OPERATE
        )

        assert (
            central_node_mid.dish_master_dict[dish_id].pointingState
            == PointingState.TRACK
        )
        assert (
            central_node_mid.dish_leaf_node_dict[dish_id].pointingState
            == PointingState.TRACK
        )
        assert check_long_running_command_status(
            central_node_mid.dish_master_dict[dish_id],
            "longRunningCommandStatus",
            "_Scan",
            "COMPLETED",
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
