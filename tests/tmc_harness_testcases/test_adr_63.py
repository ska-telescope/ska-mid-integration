"""Test module for verification """

import json

import pytest
from assertpy import assert_that
from pytest_bdd import given, scenario, then, when
from ska_tango_base.control_model import ObsState
from ska_tango_testing.integration import TangoEventTracer, log_events
from tango import DevState

from tests.resources.test_harness.central_node_mid import CentralNodeWrapperMid
from tests.resources.test_harness.constant import COMMAND_COMPLETED
from tests.resources.test_harness.event_recorder import EventRecorder
from tests.resources.test_harness.helpers import (
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
)
from tests.resources.test_harness.subarray_node import SubarrayNodeWrapper
from tests.resources.test_harness.utils.common_utils import JsonFactory

TIMEOUT = 110


@pytest.mark.batch2
@pytest.mark.SKA_mid
@scenario(
    "../features/adr_63.feature",
    "TMC behavior when configure command is invoked with ADR-63 JSON",
)
def test_tmc_configure_adr_63():
    """
    Test case to verify ADR-63 Configure functionality
    """


@given("a TMC")
def given_tmc(
    central_node_mid: CentralNodeWrapperMid,
    subarray_node: SubarrayNodeWrapper,
    event_tracer: TangoEventTracer,
):
    """Given a TMC"""
    # Setting up subscriptions
    event_tracer.subscribe_event(
        central_node_mid.central_node, "telescopeState"
    )
    event_tracer.subscribe_event(
        central_node_mid.central_node, "longRunningCommandResult"
    )
    event_tracer.subscribe_event(subarray_node.subarray_node, "obsState")
    event_tracer.subscribe_event(
        subarray_node.subarray_node, "longRunningCommandResult"
    )

    # Logging setup
    log_events(
        {
            central_node_mid.central_node: [
                "telescopeState",
                "longRunningCommandResult",
            ],
            subarray_node.subarray_node: [
                "obsState",
                "longRunningCommandResult",
            ],
        }
    )
    # TelescopeOn
    central_node_mid.move_to_on()

    # Assertions
    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION AFTER ON COMMAND: "
        "Central Node device"
        f"({central_node_mid.central_node.dev_name()}) "
        "is expected to be in TelescopeState ON",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_mid.central_node,
        "telescopeState",
        DevState.ON,
    )
    assert_that(event_tracer).described_as(
        "FAILED UNEXPECTED INITIAL OBSSTATE: "
        "Subarray Node device"
        f"({central_node_mid.subarray_node.dev_name()}) "
        "is expected to be in EMPTY obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_mid.subarray_node,
        "obsState",
        ObsState.EMPTY,
    )
    event_tracer.clear_events()


@when("the resources are assigned to TMC SubarrayNode")
def invoke_assign_resources(
    central_node_mid: CentralNodeWrapperMid,
    event_recorder: EventRecorder,
    command_input_factory: JsonFactory,
    subarray_node,
):
    """
    Move TMC Subarray to IDLE obsstate.
    :param central_node_mid: fixture for a TMC CentralNode Mid under test
    which provides simulated master devices
    :param event_recorder: fixture for a MockTangoEventCallbackGroup
    for validating the subscribing and receiving events.
    :param command_input_factory: fixture for creating input required
    for command
    :param subarray_node: fixture for a TMC SubarrayNode under test
    """
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_mid", command_input_factory
    )
    event_recorder.subscribe_event(
        central_node_mid.central_node, "longRunningCommandResult"
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
        (unique_id[0], COMMAND_COMPLETED),
        lookahead=5,
    )


@when("the Configure command is invoked with respective ADR-63 changes input")
def invoke_configure(
    subarray_node: SubarrayNodeWrapper,
    command_input_factory: JsonFactory,
    event_recorder: EventRecorder,
) -> None:
    """
    Invokes Configure command on TMC SubarrayNode
    """
    event_recorder.subscribe_event(
        subarray_node.subarray_node, "longRunningCommandResult"
    )
    configure_input_json = prepare_json_args_for_commands(
        "configure_adr_63", command_input_factory
    )
    subarray_node.execute_transition("Configure", argin=configure_input_json)


@then("the TMC SubarrayNode transitions to obsState READY")
def verify_ready_obsstate(
    subarray_node: SubarrayNodeWrapper,
    command_input_factory: JsonFactory,
    event_recorder: EventRecorder,
) -> None:

    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.READY,
    )
