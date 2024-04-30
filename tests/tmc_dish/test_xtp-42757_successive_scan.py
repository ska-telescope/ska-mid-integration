"""Test module for TMC-DISH Configure functionality"""

import json
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


@pytest.mark.tmc_dish
@scenario(
    "../features/tmc_dish/xtp-42757_successive_scan.feature",
    "Testing of successive Scan functionality for tmc-dish interface",
)
def test_tmc_dish_successive_scan_with_different_scan_duration():
    """
    Test case to verify TMC-DISH successive Scab functionality
    with different receiver band and scan duration.

    Glossary:
        - "central_node_mid": fixture for a TMC CentralNode under test
        - "simulator_factory": fixture for SimulatorFactory class,
        which provides simulated master devices
        - "event_recorder": fixture for EventRecorder class
    """


@given("a Telescope in ON state and TMC subarray in IDLE obsState")
def turn_on_telescope(
    central_node_mid,
    event_recorder,
    simulator_factory,
    subarray_node,
    command_input_factory,
):
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
    event_recorder.subscribe_event(
        central_node_mid.dish_master_dict["SKA001"], "PointingState"
    )
    event_recorder.subscribe_event(
        central_node_mid.dish_master_dict["SKA036"], "PointingState"
    )
    event_recorder.subscribe_event(
        central_node_mid.dish_master_dict["SKA063"], "PointingState"
    )
    event_recorder.subscribe_event(
        central_node_mid.dish_master_dict["SKA100"], "PointingState"
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
        "the command Configure is issued to the TMC"
        + " subarray with {receiver_band1} and {scan_duration1} sec"
    )
)
def invoke_configure(
    subarray_node, command_input_factory, receiver_band1, scan_duration1
):
    """
    A method to invoke Configure command
    """
    configure_input_json = prepare_json_args_for_commands(
        "configure_mid", command_input_factory
    )
    configure_input = json.loads(configure_input_json)
    configure_input["dish"]["receiver_band"] = receiver_band1
    configure_input["tmc"]["scan_duration"] = float(scan_duration1)
    subarray_node.execute_transition("Configure", json.dumps(configure_input))


@then("the TMC subarray transitions to obsState READY")
@given("the TMC subarray transitions to obsState READY")
def check_dish_mode_and_pointing_state(
    subarray_node, event_recorder, central_node_mid
):
    """
    Method to check dishMode and pointingState of DISH and
    SubarrayNode obsState.
    """
    assert event_recorder.has_change_event_occurred(
        central_node_mid.dish_master_dict["SKA001"],
        "PointingState",
        PointingState.TRACK,
        lookahead=5,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.dish_master_dict["SKA036"],
        "PointingState",
        PointingState.TRACK,
        lookahead=5,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.dish_master_dict["SKA063"],
        "PointingState",
        PointingState.TRACK,
        lookahead=5,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.dish_master_dict["SKA100"],
        "PointingState",
        PointingState.TRACK,
        lookahead=5,
    )

    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node, "obsState", ObsState.READY, lookahead=10
    )


@then("with command Scan TMC subarray transitions to obsState SCANNING")
@given("with command Scan TMC subarray transitions to obsState SCANNING")
def invoke_scan(subarray_node, command_input_factory, event_recorder):
    """
    A method to invoke Scan command
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
    """
    time.sleep(scan_duration1)
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node, "obsState", ObsState.READY, lookahead=10
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
    """
    time.sleep(scan_duration2)
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node, "obsState", ObsState.READY, lookahead=10
    )


@given("with command End TMC subarray transitions to obsState IDLE")
def invoke_end_command(subarray_node, event_recorder):
    """
    This method invokes End command
    """
    subarray_node.execute_transition("End")
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node, "obsState", ObsState.IDLE, lookahead=10
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
    """
    configure_input_json = prepare_json_args_for_commands(
        "configure_mid", command_input_factory
    )
    configure_input = json.loads(configure_input_json)
    configure_input["dish"]["receiver_band"] = receiver_band2
    configure_input["tmc"]["scan_duration"] = float(scan_duration2)
    subarray_node.execute_transition("Configure", json.dumps(configure_input))
