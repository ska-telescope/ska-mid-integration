"""Test module to test TMC-CSP End functionality."""
import json
import logging

import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState
from tango import DevState

from tests.resources.test_harness.central_node_mid import CentralNodeWrapperMid
from tests.resources.test_harness.event_recorder import EventRecorder
from tests.resources.test_harness.helpers import (
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
)
from tests.resources.test_harness.subarray_node import SubarrayNodeWrapper
from tests.resources.test_harness.utils.common_utils import JsonFactory

LOGGER = logging.getLogger(__name__)


@pytest.mark.skip(reason="Requires CBF chart with ska-telmodel v.1.15.0")
@pytest.mark.tmc_csp
@scenario(
    "../features/tmc_csp/xtp_29374_end.feature",
    "End configure from CSP Subarray using TMC",
)
def test_tmc_csp_end_functionality() -> None:
    """
    Test case to verify TMC-CSP observation End functionality
    """


@given("the telescope is in ON state")
def check_telescope_is_in_on_state(
    central_node_mid: CentralNodeWrapperMid, event_recorder: EventRecorder
) -> None:
    """Ensure telescope is in ON state."""
    if central_node_mid.telescope_state != "ON":
        central_node_mid.wait.set_wait_for_csp_master_to_become_off()
        central_node_mid.csp_master.adminMode = 0
        central_node_mid.wait.wait(500)
        central_node_mid.move_to_on()
    event_recorder.subscribe_event(
        central_node_mid.central_node, "telescopeState"
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "telescopeState",
        DevState.ON,
        lookahead=15,
    )


@given(parsers.parse("TMC subarray {subarray_id} is in READY ObsState"))
def move_subarray_node_to_ready_obsstate(
    central_node_mid: CentralNodeWrapperMid,
    subarray_node: SubarrayNodeWrapper,
    event_recorder: EventRecorder,
    command_input_factory: JsonFactory,
    subarray_id: str,
) -> None:
    """Move TMC Subarray to READY obsstate."""
    central_node_mid.set_subarray_id(subarray_id)
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_mid", command_input_factory
    )
    # Create json for AssignResources commands with requested subarray_id
    assign_input = json.loads(assign_input_json)
    assign_input["subarray_id"] = int(subarray_id)
    central_node_mid.perform_action(
        "AssignResources", json.dumps(assign_input)
    )

    event_recorder.subscribe_event(central_node_mid.subarray_node, "obsState")
    assert event_recorder.has_change_event_occurred(
        central_node_mid.subarray_node,
        "obsState",
        ObsState.IDLE,
        lookahead=20,
    )
    configure_input_json = prepare_json_args_for_commands(
        "configure_mid", command_input_factory
    )
    subarray_node.execute_transition("Configure", argin=configure_input_json)
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.READY,
        lookahead=20,
    )


@when(parsers.parse("I issue End command to TMC subarray {subarray_id}"))
def invoke_end_command(subarray_node: SubarrayNodeWrapper) -> None:
    """Invoke End command."""
    subarray_node.execute_transition("End")


@then(parsers.parse("the CSP subarray transitions to ObsState IDLE"))
def check_if_csp_subarray_moved_to_idle_obsstate(
    subarray_node: SubarrayNodeWrapper, event_recorder
):
    """Ensure CSP subarray is moved to IDLE obsstate"""
    event_recorder.subscribe_event(
        subarray_node.subarray_devices["csp_subarray"], "obsState"
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_devices["csp_subarray"],
        "obsState",
        ObsState.IDLE,
    )


@then(
    parsers.parse(
        "the TMC subarray {subarray_id} transitions to ObsState IDLE"
    )
)
def check_if_tmc_subarray_moved_to_idle_obsstate(
    subarray_node: SubarrayNodeWrapper, event_recorder: EventRecorder
) -> None:
    """Ensure TMC Subarray is moved to IDLE obsstate"""
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.IDLE,
        lookahead=20,
    )
