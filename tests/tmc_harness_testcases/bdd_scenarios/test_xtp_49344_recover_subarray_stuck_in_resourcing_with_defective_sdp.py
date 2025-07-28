"""Test module to test Assignresources while SDP is defective."""

import pytest
from pytest_bdd import given, parsers, scenario
from ska_control_model import ObsState
from ska_tango_testing.mock.placeholders import Anything

from tests.resources.test_harness.central_node_mid import CentralNodeWrapperMid
from tests.resources.test_harness.event_recorder import EventRecorder
from tests.resources.test_harness.helpers import (
    get_device_simulators,
    prepare_json_args_for_centralnode_commands,
)
from tests.resources.test_harness.simulator_factory import SimulatorFactory
from tests.resources.test_harness.subarray_node import SubarrayNodeWrapper
from tests.resources.test_harness.utils.common_utils import JsonFactory
from tests.resources.test_support.constant import (
    RESET_DEFECT,
    SDP_BACK_TO_INITIAL_STATE,
)


@pytest.mark.batch1
@pytest.mark.SKA_mid
@scenario(
    "../features/test_harness/"
    + "xtp_49344_recover_subarray_stuck_in_resourcing.feature",
    "TMC behavior when subarray stuck in obsState FAULT",
)
def test_recover_subarray_stuck_in_resourcing() -> None:
    """
    Test case to verify Assignresources with SDP is defective.
    """


# from conftest.py
# @given("the telescope is in ON state")


@given(parsers.parse("TMC subarray {subarray_id} busy in assigning resources"))
def telescope_is_in_resourcing_obsstate(
    central_node_mid: CentralNodeWrapperMid,
    subarray_node_mid: SubarrayNodeWrapper,
    event_recorder: EventRecorder,
    command_input_factory: JsonFactory,
    simulator_factory: SimulatorFactory,
    subarray_id: str,
):
    """A method to check if telescope in is resourcing obsSstate."""
    central_node_mid.set_subarray_id(subarray_id)

    event_recorder.subscribe_event(
        central_node_mid.central_node, "longRunningCommandResult"
    )
    event_recorder.subscribe_event(subarray_node_mid.subarray_node, "obsState")

    # Induce fault on SDP Subarry so that it raises exception and
    # returns to the obsState EMPTY
    _, sdp_sim, _, _, _, _ = get_device_simulators(simulator_factory)
    sdp_sim.SetDefective(SDP_BACK_TO_INITIAL_STATE)
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_mid", command_input_factory
    )

    pytest.command_result = central_node_mid.perform_action(
        "AssignResources", assign_input_json
    )


@given("SDP subarray raised error goes back to obsState EMPTY")
def sdp_subarray_stuck_is_in_empty(
    central_node_mid: CentralNodeWrapperMid,
    event_recorder: EventRecorder,
    simulator_factory: SimulatorFactory,
):
    "Method to check SDP subarray is in EMPTY."
    _, sdp_sim, _, _, _, _ = get_device_simulators(simulator_factory)
    event_recorder.subscribe_event(sdp_sim, "obsState")
    assert event_recorder.has_change_event_occurred(
        sdp_sim,
        "obsState",
        ObsState.EMPTY,
    )
    event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "longRunningCommandResult",
        (pytest.command_result[1][0], Anything),
        lookahead=15,
    )
    sdp_sim.SetDefective(RESET_DEFECT)


# from conftest.py
# @given("CSP subarray transitioned to obsState IDLE")
# @given("CSP subarray transitioned to obsState IDLE")
# @when("I invoked Abort on TMC subarray {subarray_id}")
# @then("the CSP subarray and SDP subarray transitions to ObsState ABORTED")
# @then("the TMC subarray {subarray_id} transitions to ObsState ABORTED")
