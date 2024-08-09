"""Test module to test Assignresources while CSP is defective."""
import json

import pytest
from pytest_bdd import given, parsers, scenario, then
from ska_control_model import ObsState
from ska_tango_testing.mock.placeholders import Anything

from tests.resources.test_harness.central_node_mid import CentralNodeWrapperMid
from tests.resources.test_harness.constant import (
    COMMAND_FAILED_WITH_EXCEPTION_OBSSTATE_EMPTY,
)
from tests.resources.test_harness.event_recorder import EventRecorder
from tests.resources.test_harness.helpers import (
    get_device_simulators,
    prepare_json_args_for_centralnode_commands,
)
from tests.resources.test_harness.utils.common_utils import JsonFactory


@pytest.mark.test1
@pytest.mark.SKA_mid
@scenario(
    "../features/test_harness/xtp-49348_test_recover_"
    + "subarray_stuck_in_resourcing_with_csp_empty_with_abort.feature",
    "TMC behavior when subarray stuck in obsState RESOURCING",
)
def test_recover_subarray_stuck_in_resourcing_with_defective_csp() -> None:
    """
    Test case to verify Assignresources with CSP is defective.
    """


# from conftest.py
# @given("the telescope is in ON state")


@given(parsers.parse("TMC subarray {subarray_id} busy in assigning resources"))
def telescope_is_in_resourcing_obsstate(
    central_node_mid: CentralNodeWrapperMid,
    event_recorder: EventRecorder,
    command_input_factory: JsonFactory,
    simulator_factory,
    subarray_id: str,
):
    """A method to check if telescope in is resourcing obsSstate."""
    central_node_mid.set_subarray_id(subarray_id)
    csp_sim, _, _, _, _, _ = get_device_simulators(simulator_factory)

    event_recorder.subscribe_event(
        central_node_mid.central_node, "longRunningCommandResult"
    )
    # After AssignResources invocation, CSP Subarray first transtions to
    # obsState RESOURCING and then to the obsState EMPTY due to fault injection
    csp_sim.SetDefective(
        json.dumps(COMMAND_FAILED_WITH_EXCEPTION_OBSSTATE_EMPTY)
    )
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_mid", command_input_factory
    )

    pytest.command_result = central_node_mid.perform_action(
        "AssignResources", assign_input_json
    )


@given("CSP subarray raised error goes back to obsState EMPTY")
def sdp_subarray_stuck_is_in_empty(
    event_recorder: EventRecorder,
    simulator_factory: JsonFactory,
    central_node_mid: CentralNodeWrapperMid,
):
    "Method to check SDP subarray is in EMPTY."
    event_recorder.subscribe_event(
        central_node_mid.central_node, "longRunningCommandResult"
    )

    csp_sim, _, _, _, _, _ = get_device_simulators(simulator_factory)
    event_recorder.subscribe_event(csp_sim, "obsState")
    assert event_recorder.has_change_event_occurred(
        csp_sim,
        "obsState",
        ObsState.EMPTY,
    )
    assertion_data = event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "longRunningCommandResult",
        (pytest.command_result[1][0], Anything),
        lookahead=15,
    )
    exception_message = (
        "Exception occurred on the following devices: "
        + "ska_mid/tm_leaf_node/csp_subarray01: "
    )
    assert (
        exception_message
        in json.loads(assertion_data["attribute_value"][1])[1]
    )


@given("SDP subarray transitioned to obsState IDLE")
def csp_subarray_is_in_idle(
    event_recorder: EventRecorder, simulator_factory: JsonFactory
):
    "Method to check CSP subarray is in IDLE."
    _, sdp_sim, _, _, _, _ = get_device_simulators(simulator_factory)
    event_recorder.subscribe_event(sdp_sim, "obsState")
    assert event_recorder.has_change_event_occurred(
        sdp_sim,
        "obsState",
        ObsState.IDLE,
    )


# from conftest.py
# @given("CSP subarray transitioned to obsState IDLE")
# @when("I invoked Abort on TMC subarray {subarray_id}")
# @then("the TMC subarray {subarray_id} transitions to ObsState ABORTED")


@then("the SDP subarray transitions to ObsState ABORTED")
def sdp_csp_subarray_is_in_aborted_obsstate(
    event_recorder: EventRecorder, simulator_factory: JsonFactory
):
    """
    Method to check SDP subarray and CSP subarray is in ABORTED obsstate
    """
    csp_sim, sdp_sim, _, _, _, _ = get_device_simulators(simulator_factory)
    event_recorder.subscribe_event(sdp_sim, "obsState")
    event_recorder.subscribe_event(csp_sim, "obsState")

    assert event_recorder.has_change_event_occurred(
        sdp_sim,
        "obsState",
        ObsState.ABORTED,
    )
