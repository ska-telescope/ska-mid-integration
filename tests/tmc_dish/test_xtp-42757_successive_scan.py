"""Test module for TMC-DISH Configure functionality"""

import json
import time

import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_tango_base.control_model import ObsState

from tests.resources.test_harness.constant import COMMAND_COMPLETED
from tests.resources.test_harness.helpers import (
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
)
from tests.resources.test_support.enum import DishMode, PointingState

<<<<<<< HEAD

<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
@pytest.mark.skip(reason="Dish pointingstate issue")
=======
@pytest.mark.skip
>>>>>>> 1664808f (SAH-1564: Test pipline)
=======
>>>>>>> f5031dbd (SAH-1564: Test pipline)
=======
@pytest.mark.MM
>>>>>>> e96d445e (SAH-1564: Testing integration test case)
=======
>>>>>>> 7e974b16 (SAH-1564: Update test case for dish side)
=======
@pytest.mark.skip
>>>>>>> 22caffec (SAH-1564: Run only long sequence test for tmc-dish interface)
=======
>>>>>>> 53d94e03 (SAH-1564: Enable tmc-dish bdd tests)
=======
@pytest.mark.skip(reason="Test being fix in SAH-1564")
>>>>>>> 00483018 (SAH-1536: Update test case)
@pytest.mark.tmc_dish
@scenario(
    "../features/tmc_dish/xtp-42757_successive_scan.feature",
    "Testing of successive Scan functionality for tmc-dish interface",
)
def test_tmc_dish_successive_scan_with_different_scan_duration():
    """
    Test case to verify TMC-DISH successive Scab functionality
    with different receiver band and scan duration.
    """


@given("TMC subarray is in IDLE obsState")
def check_subarray_obsState_idle(
    subarray_node, central_node_mid, event_recorder, command_input_factory
):
    """
    Method to check subarray is in IDLE obsState

    Args:
        subarray_node: Fixture for a Subarray Node wrapper class
        central_node_mid: Fixture for a TMC CentralNode wrapper class
        event_recorder: Fixture for EventRecorder class
        command_input_factory: fixture for creating input required
        for command
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
        (pytest.command_result[1][0], COMMAND_COMPLETED),
    )


@given(
    parsers.parse(
        "the command Configure is issued to the TMC"
        + " subarray with {receiver_band1} and {scan_duration1} sec"
    )
)
def invoke_configure(
    subarray_node, command_input_factory, receiver_band1, scan_duration1
):
    """
    A method to invoke Configure command

    Args:
        subarray_node: Fixture for a Subarray Node wrapper class
        command_input_factory: fixture for creating input required
        for command
        receiver_band1(str) : receiver band for configure command
        scan_duration1 (str): scan duration required
    """

    configure_input_json = prepare_json_args_for_commands(
        "configure_mid", command_input_factory
    )
    configure_input = json.loads(configure_input_json)
    configure_input["dish"]["receiver_band"] = receiver_band1
    configure_input["tmc"]["scan_duration"] = float(scan_duration1)
    pytest.command_result = subarray_node.execute_transition(
        "Configure", json.dumps(configure_input)
    )


@then("the TMC subarray transitions to obsState READY")
@given("the TMC subarray transitions to obsState READY")
def check_dish_mode_and_pointing_state(
    subarray_node, event_recorder, central_node_mid
):
    """
    Method to check dishMode and pointingState of DISH and
    SubarrayNode obsState.

    Args:
        subarray_node: Fixture for a Subarray Node wrapper class
        subarray_id (str): Subarray ID
        event_recorder: Fixture for EventRecorder class
        central_node_mid: Fixture for a TMC CentralNode wrapper class
    """

    for dish_id in ["SKA001", "SKA036", "SKA063", "SKA100"]:
        assert event_recorder.has_change_event_occurred(
            central_node_mid.dish_master_dict[dish_id],
            "dishMode",
            DishMode.OPERATE,
            lookahead=15,
        )
        assert event_recorder.has_change_event_occurred(
            central_node_mid.dish_leaf_node_dict[dish_id],
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
        assert event_recorder.has_change_event_occurred(
            central_node_mid.dish_leaf_node_dict[dish_id],
            "pointingState",
            PointingState.TRACK,
            lookahead=15,
        )
    event_recorder.subscribe_event(
        subarray_node.subarray_node, "longRunningCommandResult"
    )
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
        subarray_node.subarray_node,
        "obsState",
        ObsState.READY,
        lookahead=10,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "longRunningCommandResult",
        (pytest.command_result[1][0], COMMAND_COMPLETED),
    )


@then("with command Scan TMC subarray transitions to obsState SCANNING")
@given("with command Scan TMC subarray transitions to obsState SCANNING")
def invoke_scan(subarray_node, command_input_factory, event_recorder):
    """
    A method to invoke Scan command

    Args:
        subarray_node: Fixture for a Subarray Node wrapper class
        command_input_factory: fixture for creating input required
        for command
        event_recorder: Fixture for EventRecorder class
    """

    scan_input_json = prepare_json_args_for_commands(
        "scan_mid", command_input_factory
    )
    subarray_node.execute_transition("Scan", scan_input_json)

    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.SCANNING,
        lookahead=10,
    )


@given(
    parsers.parse(
        "the TMC subarray transitions to obsState READY when scan"
        + " duration {scan_duration1} is over"
    )
)
def check_automatic_endscan_with_scan_duration1(
    subarray_node, event_recorder, scan_duration1
):
    """
    A method to check if EndScan is successful.

    Args:
        subarray_node: Fixture for a Subarray Node wrapper class
        event_recorder: Fixture for EventRecorder class
        scan_duration1 (str): scan duration required
    """
    time.sleep(int(scan_duration1))
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node, "obsState", ObsState.READY, lookahead=15
    )


@then(
    parsers.parse(
        "the TMC subarray transitions to obsState READY when scan"
        + " duration {scan_duration2} is over"
    )
)
def check_automatic_endscan_with_scan_duration2(
    subarray_node, event_recorder, scan_duration2
):
    """
    A method to check if EndScan is successful.

    Args:
        subarray_node: Fixture for a Subarray Node wrapper class
        event_recorder: Fixture for EventRecorder class
        scan_duration2 (str): scan duration required
    """
    time.sleep(int(scan_duration2))
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node, "obsState", ObsState.READY, lookahead=15
    )


@given("with command End TMC subarray transitions to obsState IDLE")
def invoke_end_command(subarray_node, event_recorder, central_node_mid):
    """
    This method invokes End command

    Args:
        subarray_node: Fixture for a Subarray Node wrapper class
        event_recorder: Fixture for EventRecorder class
        central_node_mid: Fixture for a TMC CentralNode wrapper class
    """
    pytest.command_result = subarray_node.execute_transition("End")

    for dish_id in ["SKA001", "SKA036", "SKA063", "SKA100"]:
        assert event_recorder.has_change_event_occurred(
            central_node_mid.dish_master_dict[dish_id],
            "pointingState",
            PointingState.READY,
            lookahead=15,
        )

        assert event_recorder.has_change_event_occurred(
            central_node_mid.dish_leaf_node_dict[dish_id],
            "pointingState",
            PointingState.READY,
            lookahead=15,
        )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node, "obsState", ObsState.IDLE, lookahead=10
    )

    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "longRunningCommandResult",
        (pytest.command_result[1][0], COMMAND_COMPLETED),
    )


@when(
    parsers.parse(
        "the next configure command is issued to the TMC"
        + " subarray with {receiver_band2} and {scan_duration2} sec"
    )
)
def invoke_next_configure(
    subarray_node, command_input_factory, receiver_band2, scan_duration2
):
    """
    A method to invoke Configure command

    Args:
        subarray_node: Fixture for a Subarray Node wrapper class
        command_input_factory: fixture for creating input required
        for command
        receiver_band2 (str) : receiver band for configure command
        scan_duration2 (str) : scan duration required

    """
    configure_input_json = prepare_json_args_for_commands(
        "configure_mid", command_input_factory
    )
    configure_input = json.loads(configure_input_json)
    configure_input["dish"]["receiver_band"] = receiver_band2
    configure_input["tmc"]["scan_duration"] = float(scan_duration2)
    configure_input["csp"]["common"]["frequency_band"] = receiver_band2

    pytest.command_result = subarray_node.execute_transition(
        "Configure", json.dumps(configure_input)
    )
