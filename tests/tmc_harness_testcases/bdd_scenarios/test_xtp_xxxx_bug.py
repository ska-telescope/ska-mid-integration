"""Test module to test delay functionality."""
import json
import logging

import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState
from ska_telmodel.schema import validate as telmodel_validate
from tango import DevState

from tests.conftest import MID_DELAY_JSON, MID_DELAYMODEL_VERSION
from tests.resources.test_harness.central_node_mid import CentralNodeWrapperMid
from tests.resources.test_harness.event_recorder import EventRecorder
from tests.resources.test_harness.helpers import (
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
)
from tests.resources.test_harness.subarray_node import SubarrayNodeWrapper
from tests.resources.test_harness.utils.common_utils import JsonFactory

LOGGER = logging.getLogger(__name__)


@pytest.mark.m1
@pytest.mark.SKA_mid
@scenario(
    "../features/test_harness/xtp_xxxx_verify_bug.feature",
    "Verify generated delay epoch values are less than delay advance time",
)
def test_tmc_csp_delay_functionality() -> None:
    """
    Test case to verify delay generates properly.
    """


@given("the telescope is in ON state")
def check_telescope_is_in_on_state(
    central_node_mid: CentralNodeWrapperMid, event_recorder: EventRecorder
) -> None:
    """Ensure telescope is in ON state."""
    central_node_mid.move_to_on()
    event_recorder.subscribe_event(
        central_node_mid.central_node, "telescopeState"
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "telescopeState",
        DevState.ON,
    )


@given(parsers.parse("TMC subarray {subarray_id} in ObsState IDLE"))
def move_subarray_node_to_idle_obsstate(
    central_node_mid: CentralNodeWrapperMid,
    event_recorder: EventRecorder,
    command_input_factory: JsonFactory,
    subarray_id: str,
) -> None:
    """Move TMC Subarray to IDLE ObsState."""
    central_node_mid.set_subarray_id(subarray_id)
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_mid", command_input_factory
    )
    # Create json for AssignResources commands with requested subarray_id
    assign_input = json.loads(assign_input_json)
    assign_input["subarray_id"] = int(subarray_id)
    central_node_mid.store_resources(json.dumps(assign_input))

    event_recorder.subscribe_event(central_node_mid.subarray_node, "obsState")
    assert event_recorder.has_change_event_occurred(
        central_node_mid.subarray_node,
        "obsState",
        ObsState.IDLE,
    )


@when("I configure the TMC subarray")
def invoke_configure_command(
    subarray_node: SubarrayNodeWrapper,
    command_input_factory: JsonFactory,
    event_recorder: EventRecorder,
) -> None:
    """
    Invokes Configure command and checks whether subarray is in ObsState READY
    """
    configure_input_json = prepare_json_args_for_commands(
        "configure_mid", command_input_factory
    )
    subarray_node.store_configuration_data(configure_input_json)
    event_recorder.subscribe_event(subarray_node.subarray_node, "obsState")
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.READY,
    )


@then("Once configured is invoked delay starting generatig without wait")
def check_if_delay_values_are_generating(
    subarray_node: SubarrayNodeWrapper,
) -> None:
    """Check if delay values are generating."""
    cspsal_node = subarray_node.csp_subarray_leaf_node
    delay_json = json.loads(cspsal_node.read_attribute("delayModel").value)
    assert delay_json != json.dumps(MID_DELAY_JSON)
    telmodel_validate(
        version=MID_DELAYMODEL_VERSION,
        config=delay_json,
        strictness=2,
    )


@when("I end the observation")
def invoke_end_command(
    subarray_node: SubarrayNodeWrapper, event_recorder: EventRecorder
) -> None:
    """Invoke End command and checks whether subarray is in ObsState READY"""
    subarray_node.end_observation()
    event_recorder.subscribe_event(subarray_node.subarray_node, "obsState")
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.IDLE,
    )


@then("CSP Subarray Leaf Node stops generating delay values without waiting")
def check_if_delay_values_are_stop_generating(
    subarray_node: SubarrayNodeWrapper,
) -> None:
    """Check if delay values are stop generating."""
    cspsal_node = subarray_node.csp_subarray_leaf_node
    delay_json = json.loads(cspsal_node.read_attribute("delayModel").value)
    assert delay_json == MID_DELAY_JSON
