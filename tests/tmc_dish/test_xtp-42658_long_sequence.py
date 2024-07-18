"""Test module for long sequence functionality

This module tests the TMC-DISH long sequence functionality, ensuring that
a sequence of commands including configuration, scanning, and reconfiguration
are executed successfully and the system transitions
through the expected states.
"""
<<<<<<< HEAD

import ast
=======
>>>>>>> 98a5a250 (SAH-1536: Debug test failure)
import json
import logging

import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_tango_base.control_model import ObsState

from tests.resources.test_harness.central_node_mid import CentralNodeWrapperMid
from tests.resources.test_harness.event_recorder import EventRecorder
from tests.resources.test_harness.helpers import (
<<<<<<< HEAD
<<<<<<< HEAD
=======
    LongRunningCommandResult,
>>>>>>> 1232aef4 (SAH-1536: Resolve review comments)
=======
>>>>>>> 9e9e3c92 (SAH-1536: Resolve review comments)
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
)
from tests.resources.test_harness.subarray_node import SubarrayNodeWrapper
from tests.resources.test_harness.utils.common_utils import JsonFactory
from tests.resources.test_support.common_utils.result_code import ResultCode
from tests.resources.test_support.enum import DishMode, PointingState

<<<<<<< HEAD
# import time


configure_logging(logging.DEBUG)
LOGGER = logging.getLogger(__name__)
=======
>>>>>>> 2ee3ddf7 (SAH-1536: Enable skipped tmc-dish tests)

@pytest.mark.tmc_dish
@scenario(
    "../features/tmc_dish/xtp-42658_long_sequence.feature",
    "TMC executes long sequence of commands successfully",
)
def test_tmc_dish_long_sequence_functionality():
    """
    Test case to verify TMC-DISH long sequence functionality
    """


<<<<<<< HEAD
@given(
    parsers.parse(
        "a Telescope consisting of TMC, DISH {dish_ids},"
        + " simulated CSP and simulated SDP"
    )
)
def given_a_telescope(central_node_mid, dish_ids):
    """Given a TMC with DISH, CSP, and SDP

    Args:
        central_node_mid (CentralNode): A fixture for the CentralNode
        tango device class.
        dish_ids (str): A comma-separated string of dish IDs.

    This function verifies the connection to the CSP and SDP masters,
    and checks the connectivity of each dish's master and leaf node
    by sending a ping command.
    """
    assert central_node_mid.csp_master.ping() > 0
    assert central_node_mid.sdp_master.ping() > 0
    for dish_id in dish_ids.split(","):
        assert central_node_mid.dish_master_dict[dish_id].ping() > 0
        assert central_node_mid.dish_leaf_node_dict[dish_id].ping() > 0


@given("the Telescope is in ON state")
def turn_on_telescope(central_node_mid, event_recorder):
    """
    A method to put Telescope ON
    """
<<<<<<< HEAD
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
    for dish_id in ["SKA001", "SKA036", "SKA063", "SKA100"]:
        event_recorder.subscribe_event(
            central_node_mid.dish_master_dict[dish_id], "dishMode"
        )

<<<<<<< HEAD
        assert event_recorder.has_change_event_occurred(
            central_node_mid.dish_master_dict[dish_id],
            "dishMode",
            DishMode.STANDBY_LP,
        )
    Resource(central_node_mid.central_node).assert_attribute(
        "telescopeState"
    ).equals(["OFF", "STANDBY"])
=======
    event_recorder.subscribe_event(csp_master_sim, "State")
    event_recorder.subscribe_event(sdp_master_sim, "State")

=======
>>>>>>> 3b52eb24 (SAH-1536: Add test case for tmc-dish unavailability)
    central_node_mid.move_to_on()
    event_recorder.subscribe_event(central_node_mid.csp_master, "State")
    event_recorder.subscribe_event(central_node_mid.sdp_master, "State")

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
        event_recorder.subscribe_event(
            central_node_mid.dish_master_dict[dish_id], "dishMode"
        )
        event_recorder.subscribe_event(
            central_node_mid.dish_leaf_node_dict[dish_id], "dishMode"
        )

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

    event_recorder.subscribe_event(
        central_node_mid.central_node, "telescopeState"
    )

    assert event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "telescopeState",
        DevState.ON,
    )
>>>>>>> 7ceda8b8 (SAH-1536: Update test case for xtp-42658)


=======
>>>>>>> aca410a8 (SAH-1536: Resolve review comments)
@given("TMC subarray is in IDLE obsState")
def check_subarray_obsState_idle(
    subarray_node, central_node_mid, event_recorder, command_input_factory
):
    """
    Method to check if the TMC subarray is in IDLE obsState.

    This function subscribes to the obsState event of the subarray node and
    assigns resources to the central node. It verifies that the subarray
    transitions to the IDLE obsState and that the longRunningCommandResult
    indicates a successful execution with ResultCode.OK.

    Args:
        subarray_node : A fixture for SubarrayNode tango device class
        central_node_mid : A fixture for CentralNode tango device class
        event_recorder: A fixture for EventRecorder class
        command_input_factory: A fixture for JsonFactory class
    """
    event_recorder.subscribe_event(subarray_node.subarray_node, "obsState")
<<<<<<< HEAD
    event_recorder.subscribe_event(
        subarray_node.subarray_node, "assignedResources"
    )
    event_recorder.subscribe_event(
        central_node_mid.central_node, "longRunningCommandResult"
    )
    event_recorder.subscribe_event(
        central_node_mid.central_node, "telescopeState"
    )
    central_node_mid.set_subarray_id(subarray_id)

    central_node_mid.move_to_on()
    assert event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "telescopeState",
        DevState.ON,
    )
=======
>>>>>>> 7ceda8b8 (SAH-1536: Update test case for xtp-42658)

    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_mid", command_input_factory
    )
    pytest.command_result = central_node_mid.store_resources(assign_input_json)

    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.IDLE,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "longRunningCommandResult",
        (pytest.command_result[1][0], str(ResultCode.OK.value)),
    )
    assert subarray_node.subarray_node.assignedResources == ast.literal_eval(
        resources
    )


@when(
    parsers.parse(
        "I configure the subarray {subarray_id} with {receiver_band_1}"
    )
)
def configure_subarray(
    subarray_node: SubarrayNodeWrapper,
    central_node_mid: CentralNodeWrapperMid,
    event_recorder: EventRecorder,
    command_input_factory: JsonFactory,
    subarray_id: str,
    receiver_band_1: str,
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
    configure_input_json["dish"]["receiver_band"] = receiver_band_1
    configure_input_json["csp"]["common"]["frequency_band"] = "1"
    central_node_mid.set_subarray_id(subarray_id)
    pytest.command_result = subarray_node.store_configuration_data(
        json.dumps(configure_input_json)
    )
    for dish_id in ["SKA001", "SKA036", "SKA063", "SKA100"]:
<<<<<<< HEAD
<<<<<<< HEAD
        event_recorder.subscribe_event(
            central_node_mid.dish_master_dict[dish_id], "pointingState"
        )
        event_recorder.subscribe_event(
<<<<<<< HEAD
            central_node_mid.dish_master_dict[dish_id], "dishMode"
=======
            central_node_mid.dish_leaf_node_dict[dish_id], "pointingState"
>>>>>>> 2ee3ddf7 (SAH-1536: Enable skipped tmc-dish tests)
        )

=======
>>>>>>> 3f2e08b9 (SAH-1536: Resolve review comments)
=======
        event_recorder.subscribe_event(
            central_node_mid.dish_leaf_node_dict[dish_id],
            "longRunningCommandResult",
        )
>>>>>>> d6082288 (SAH-1536: Update tmc-dish long sequence test)
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
        logging.info(
            "longRunningCommandResult for dishmaster after configure1 %s",
            central_node_mid.dish_master_dict[
                dish_id
            ].longRunningCommandResult,
        )
        logging.info("pytest.command_result1: %s", str(pytest.command_result))
        # assert event_recorder.has_change_event_occurred(
        #     central_node_mid.dish_leaf_node_dict[dish_id],
        #     "longRunningCommandResult",
        #     (pytest.command_result[1][0], str(ResultCode.OK.value)),
        #     lookahead=15,
        # )
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
    event_recorder.subscribe_event(
        subarray_node.subarray_node, "longRunningCommandResult"
    )
    central_node_mid.set_subarray_id(subarray_id)
<<<<<<< HEAD
    pytest.command_result = subarray_node.end_observation()
=======
    pytest.command_result = subarray_node.execute_transition("End")
>>>>>>> 1232aef4 (SAH-1536: Resolve review comments)
    for dish_id in ["SKA001", "SKA036", "SKA063", "SKA100"]:
<<<<<<< HEAD
<<<<<<< HEAD
        event_recorder.subscribe_event(
            central_node_mid.dish_master_dict[dish_id], "dishMode"
=======
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
=======

>>>>>>> 2ee3ddf7 (SAH-1536: Enable skipped tmc-dish tests)
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
>>>>>>> 1a8aefae (SAH-1536: Test tmc-dish long sequence tests)
        )

        assert event_recorder.has_change_event_occurred(
            central_node_mid.dish_master_dict[dish_id],
            "dishMode",
            DishMode.STANDBY_FP,
            lookahead=12,
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
    parsers.parse(
        "I reconfigure subarray {subarray_id} with {receiver_band_2}"
    )
)
def reconfigure_subarray(
    subarray_node: SubarrayNodeWrapper,
    central_node_mid: CentralNodeWrapperMid,
    event_recorder: EventRecorder,
    command_input_factory: JsonFactory,
    subarray_id: str,
    receiver_band_2: str,
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
    configure_input_json["dish"]["receiver_band"] = receiver_band_2
    configure_input_json["csp"]["common"]["frequency_band"] = "2"
    central_node_mid.set_subarray_id(subarray_id)
    pytest.command_result = subarray_node.store_configuration_data(
        json.dumps(configure_input_json)
    )
    for dish_id in ["SKA001", "SKA036", "SKA063", "SKA100"]:
<<<<<<< HEAD
<<<<<<< HEAD
        event_recorder.subscribe_event(
            central_node_mid.dish_master_dict[dish_id], "pointingState"
        )
        event_recorder.subscribe_event(
            central_node_mid.dish_master_dict[dish_id], "dishMode"
        )
<<<<<<< HEAD

        assert event_recorder.has_change_event_occurred(
            central_node_mid.dish_master_dict[dish_id],
            "dishMode",
            DishMode.OPERATE,
            lookahead=16,
        )

=======
=======

>>>>>>> 2ee3ddf7 (SAH-1536: Enable skipped tmc-dish tests)
=======
        event_recorder.subscribe_event(
            central_node_mid.dish_leaf_node_dict[dish_id],
            "longRunningCommandResult",
        )
>>>>>>> d6082288 (SAH-1536: Update tmc-dish long sequence test)
        assert (
            central_node_mid.dish_master_dict[dish_id].dishMode
            == DishMode.OPERATE
        )
        assert (
            central_node_mid.dish_leaf_node_dict[dish_id].dishMode
            == DishMode.OPERATE
        )
<<<<<<< HEAD
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
>>>>>>> 752c8d76 (SAH-1536: Update test case for xtp-42658)
=======

>>>>>>> 2ee3ddf7 (SAH-1536: Enable skipped tmc-dish tests)
        assert event_recorder.has_change_event_occurred(
            central_node_mid.dish_master_dict[dish_id],
            "pointingState",
            PointingState.TRACK,
        )
        logging.info(
            "longRunningCommandResult for dishmaster after configure2 %s ",
            central_node_mid.dish_master_dict[
                dish_id
            ].longRunningCommandResult,
        )
        logging.info("pytest.command_result2: %s", str(pytest.command_result))
        # assert event_recorder.has_change_event_occurred(
        #     central_node_mid.dish_leaf_node_dict[dish_id],
        #     "longRunningCommandResult",
        #     (pytest.command_result[1][0], str(ResultCode.OK.value)),
        #     lookahead=15,
        # )
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
<<<<<<< HEAD
    subarray_node.store_scan_data(scan_input_json)
=======

    pytest.command_result = subarray_node.execute_transition(
        "Scan", scan_input_json
    )
>>>>>>> 9e9e3c92 (SAH-1536: Resolve review comments)

    for dish_id in ["SKA001", "SKA036", "SKA063", "SKA100"]:
        event_recorder.subscribe_event(
            central_node_mid.dish_master_dict[dish_id], "scanID"
        )
        event_recorder.subscribe_event(
<<<<<<< HEAD
            central_node_mid.dish_master_dict[dish_id], "pointingState"
        )
        event_recorder.subscribe_event(
            central_node_mid.dish_master_dict[dish_id], "dishMode"
=======
            central_node_mid.dish_master_dict[dish_id],
            "longRunningCommandResult",
        )
        event_recorder.subscribe_event(
            central_node_mid.dish_leaf_node_dict[dish_id],
            "longRunningCommandResult",
>>>>>>> e299607f (SAH-1536: Resolve review comments)
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
<<<<<<< HEAD
=======
        assert (
            central_node_mid.dish_leaf_node_dict[dish_id].pointingState
            == PointingState.TRACK
        )
<<<<<<< HEAD
        logging.info(
            "longRunningCommandResult for DishLN after scan %s",
            central_node_mid.dish_leaf_node_dict[
                dish_id
            ].longRunningCommandResult,
        )
<<<<<<< HEAD
        logging.info(
            "longRunningCommandResult for DISHmaster after scan %s",
            central_node_mid.dish_master_dict[
                dish_id
            ].longRunningCommandResult,
        )
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
=======
        time.sleep(10)
=======
        time.sleep(20)
>>>>>>> 59e38b4d (SAH-1536: Debug test failure)
        logging.info(
            "longRunningCommandResult for DishLN after scan and sleep %s",
            central_node_mid.dish_leaf_node_dict[
                dish_id
            ].longRunningCommandResult,
        )
        logging.info(
            "longRunningCommandResult for DISHmaster after scan and sleep %s",
            central_node_mid.dish_master_dict[
                dish_id
            ].longRunningCommandResult,
        )
>>>>>>> 98a5a250 (SAH-1536: Debug test failure)
=======
>>>>>>> 3d6be7fc (SAH-1536: Debug test failure)
        assert event_recorder.has_change_event_occurred(
            central_node_mid.dish_master_dict[dish_id],
            "longRunningCommandResult",
            (pytest.command_result[1][0], str(ResultCode.OK.value)),
        )
=======
        logging.info("pytest.command_result: %s", str(pytest.command_result))
>>>>>>> 09c4fc92 (SAH-1536: Debug test failure)
        assert event_recorder.has_change_event_occurred(
            central_node_mid.dish_leaf_node_dict[dish_id],
            "longRunningCommandResult",
            (pytest.command_result[1][0], str(ResultCode.OK.value)),
            lookahead=15,
        )
<<<<<<< HEAD
>>>>>>> 1232aef4 (SAH-1536: Resolve review comments)
=======
        # assert event_recorder.has_change_event_occurred(
        #     central_node_mid.dish_leaf_node_dict[dish_id],
        #     "longRunningCommandResult",
        #     (pytest.command_result[1][0], str(ResultCode.OK.value)),
        # )
>>>>>>> 1003daaa (SAH-1536: Resolve review comments)
=======
>>>>>>> 98a5a250 (SAH-1536: Debug test failure)
=======
>>>>>>> 0031d69e (SAH-1536: Test pipeline)


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
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.READY,
        lookahead=10,
    )
