import json

import pytest
from pytest_bdd import given, scenario, then, when
from ska_control_model import ObsState
from ska_tango_base.control_model import HealthState
from tango import DevState

from tests.resources.test_harness.central_node_mid import CentralNodeWrapperMid
from tests.resources.test_harness.event_recorder import EventRecorder
from tests.resources.test_harness.helpers import (
    check_for_device_command_event,
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
)
from tests.resources.test_harness.utils.common_utils import JsonFactory
from tests.resources.test_support.common_utils.result_code import ResultCode


@pytest.mark.aki
@pytest.mark.SKA_mid
@scenario(
    "../features/dish_vcc_initialization/xtp_44894_kvalue_validation.feature",
    "TMC Validates the kValue when multiple kvalues are same",
)
def test_kvalue_validation_error_scenario():
    """This test validate that TMC is able to load the dish vcc
    configuration file provided to LoadDishCfg command.
    Validate that k-numbers set on dish masters
    Validate sysParam and sourceSysParam attribute set on csp master leaf node
    """


@given("a TMC")
def given_tmc():
    """Given a TMC"""


@given("Telescope is in ON state")
def telescope_in_on_state(central_node_mid, event_recorder):
    """Move Telescope to ON state
    Args
    :param central_node_mid: fixture for a TMC CentralNode Mid under test
    which provides simulated master devices
    :param event_recorder: fixture for a MockTangoEventCallbackGroup
    for validating the subscribing and receiving events.
    """
    event_recorder.subscribe_event(
        central_node_mid.central_node, "telescopeState"
    )
    central_node_mid.move_to_on()
    assert event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "telescopeState",
        DevState.ON,
    )


@when("I issue the command LoadDishCfg on TMC with multiple same kValue")
def invoke_load_dish_cfg(
    central_node_mid, event_recorder, command_input_factory
):
    """Call load_dish_cfg method which invoke LoadDishCfg
    command on CentralNode
    Args:
    :param central_node_mid: fixture for a TMC CentralNode Mid under test
    which provides simulated master devices
    :param event_recorder: fixture for a MockTangoEventCallbackGroup
    for validating the subscribing and receiving events.
    :param command_input_factory: fixture for creating input required
    for command
    """
    # Subscribe for longRunningCommandResult attribute
    event_recorder.subscribe_event(
        central_node_mid.central_node, "longRunningCommandResult"
    )
    # Prepare input for load dish configuration
    load_dish_cfg_json = prepare_json_args_for_centralnode_commands(
        "multiple_same_kval", command_input_factory
    )

    _, unique_id = central_node_mid.load_dish_vcc_configuration(
        load_dish_cfg_json
    )

    assert event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "longRunningCommandResult",
        (unique_id[0], str(int(ResultCode.OK))),
        lookahead=5,
    )


@when("TMC subarray in ObsState IDLE")
def move_subarray_node_to_idle_obsstate(
    central_node_mid: CentralNodeWrapperMid,
    event_recorder: EventRecorder,
    command_input_factory: JsonFactory,
    subarray_node,
) -> None:
    """Move TMC Subarray to IDLE obsstate."""
    event_recorder.subscribe_event(
        subarray_node.subarray_node, "longRunningCommandResult"
    )
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_mid", command_input_factory
    )
    # Create json for AssignResources commands with requested subarray_id
    assign_input = json.loads(assign_input_json)
    _, unique_id = central_node_mid.store_resources(json.dumps(assign_input))

    event_recorder.subscribe_event(central_node_mid.subarray_node, "obsState")
    assert event_recorder.has_change_event_occurred(
        central_node_mid.subarray_node,
        "obsState",
        ObsState.IDLE,
        lookahead=10,
    )

    assert event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "longRunningCommandResult",
        (unique_id[0], str(int(ResultCode.OK))),
        lookahead=5,
    )


@when("I invoke Configure command on TMC")
def invoke_configure(
    subarray_node,
    command_input_factory,
):
    """A method to invoke Configure command"""
    input_json = prepare_json_args_for_commands(
        "configure_mid", command_input_factory
    )
    pytest.result, pytest.unique_id = subarray_node.execute_transition(
        "Configure", argin=input_json
    )
    assert pytest.unique_id[0].endswith("Configure")
    assert pytest.result[0] == ResultCode.QUEUED


@then("the command is failed and the health state of the subarray is DEGRADED")
def test_tmc_rejects_command_with_error(subarray_node, event_recorder):
    """Test validate that command failed with error message"""
    event_recorder.subscribe_event(
        subarray_node.subarray_node, "longRunningCommandResult"
    )
    exception_message = "K-values must be either all same or all different"
    assert check_for_device_command_event(
        subarray_node.subarray_node,
        "longRunningCommandResult",
        exception_message,
        event_recorder,
        "Configure",
    )
    event_recorder.subscribe_event(subarray_node.subarray_node, "healthState")
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "healthState",
        HealthState.DEGRADED,
    )
