import json

import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState
from ska_tango_testing.mock.placeholders import Anything
from tango import DevState

from tests.conftest import LOGGER
from tests.resources.test_harness.constant import (
    OBS_STATE_RESOURCING_STUCK_DEFECT,
)
from tests.resources.test_harness.helpers import (
    get_device_simulators,
    prepare_json_args_for_centralnode_commands,
)


@pytest.mark.skip(
    reason="Failure is not getting simulated due to latest tmc-common package"
)
@pytest.mark.SKA_mid
@scenario(
    "../features/xtp-28282.feature",
    "TMC behavior when Csp Subarray is stuck in obsState RESOURCING",
)
def test_assign_resources_handling_on_csp_subarray_obsstate_resourcing_failure(
    central_node_mid, event_recorder, simulator_factory
):
    """
    Test to verify TMC failure handling when AssignResources
    command fails on CSP Subarray. AssignResources completes
    on SDP Subarray and it transtions to obsState IDLE.
    Whereas CSP Subarray is stuck in obsState RESOURCING.
    As a handling Abort + Restart command sequence is executed on
    the Subarray to take it to the initial obsState EMPTY.
    Glossary:
    - "central_node_mid": fixture for a TMC CentralNode Mid under test
    which provides simulated master devices
    - "event_recorder": fixture for a MockTangoEventCallbackGroup
    for validating the subscribing and receiving events.
    - "simulator_factory": fixture for creating simulator devices for
    mid Telescope respectively.
    """


@given("a TMC")
def given_tmc(central_node_mid, event_recorder):
    event_recorder.subscribe_event(
        central_node_mid.central_node, "telescopeState"
    )
    event_recorder.subscribe_event(central_node_mid.subarray_node, "obsState")
    central_node_mid.move_to_on()
    assert event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "telescopeState",
        DevState.ON,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.subarray_node,
        "obsState",
        ObsState.EMPTY,
    )


@given(
    parsers.parse(
        "the TMC SubarrayNode {subarray_id} assign resources is in progress"
    )
)
def given_tmc_subarray_assign_resources_is_in_progress(
    central_node_mid, event_recorder, simulator_factory, command_input_factory
):
    csp_sim, sdp_sim, _, _, _, _ = get_device_simulators(simulator_factory)
    event_recorder.subscribe_event(csp_sim, "obsState")
    event_recorder.subscribe_event(sdp_sim, "obsState")
    event_recorder.subscribe_event(central_node_mid.subarray_node, "obsState")
    event_recorder.subscribe_event(
        central_node_mid.central_node, "longRunningCommandResult"
    )

    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_mid", command_input_factory
    )

    # Induce fault on CSP Subarray so that it is stuck in obsState RESOURCING
    csp_sim.SetDefective(json.dumps(OBS_STATE_RESOURCING_STUCK_DEFECT))
    _, unique_id = central_node_mid.perform_action(
        "AssignResources", assign_input_json
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.subarray_node,
        "obsState",
        ObsState.RESOURCING,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "longRunningCommandResult",
        (unique_id[0], Anything),
    )


@given(parsers.parse("Sdp Subarray {subarray_id} completes assignResources"))
def sdp_subarray_assign_resources_complete(event_recorder, simulator_factory):
    _, sdp_sim, _, _, _, _ = get_device_simulators(simulator_factory)
    event_recorder.subscribe_event(sdp_sim, "obsState")
    assert event_recorder.has_change_event_occurred(
        sdp_sim,
        "obsState",
        ObsState.IDLE,
    )


@given(
    parsers.parse("Csp Subarray {subarray_id} is stuck in obsState RESOURCING")
)
def csp_subarray_stuck_in_resourcing(event_recorder, simulator_factory):
    csp_sim, _, _, _, _, _ = get_device_simulators(simulator_factory)
    event_recorder.subscribe_event(csp_sim, "obsState")
    assert event_recorder.has_change_event_occurred(
        csp_sim,
        "obsState",
        ObsState.RESOURCING,
    )


@given(
    parsers.parse("the TMC SubarrayNode {subarray_id} stucks in RESOURCING")
)
def given_tmc_subarray_stuck_resourcing(
    central_node_mid,
    simulator_factory,
    event_recorder,
):
    event_recorder.subscribe_event(central_node_mid.subarray_node, "obsState")
    LOGGER.info(
        f"SubarrayNode ObsState is: {central_node_mid.subarray_node.obsState}"
    )
    assert central_node_mid.subarray_node.obsState == ObsState.RESOURCING

    csp_sim, _, _, _, _, _ = get_device_simulators(simulator_factory)
    csp_sim.SetDefective(json.dumps({"enabled": False}))


@when(
    parsers.parse(
        "I issue the Abort command on TMC SubarrayNode {subarray_id}"
    )
)
def send_command_abort(central_node_mid):
    central_node_mid.subarray_node.Abort()


@then(
    parsers.parse(
        "the CSP, SDP and TMC subarray {subarray_id} transitions to "
        + "obsState ABORTED"
    )
)
def subarray_transitions_to_aborted(
    central_node_mid, simulator_factory, event_recorder
):
    csp_sim, sdp_sim, _, _, _, _ = get_device_simulators(simulator_factory)
    event_recorder.subscribe_event(csp_sim, "obsState")
    assert event_recorder.has_change_event_occurred(
        csp_sim,
        "obsState",
        ObsState.ABORTED,
    )
    event_recorder.subscribe_event(sdp_sim, "obsState")
    assert event_recorder.has_change_event_occurred(
        sdp_sim,
        "obsState",
        ObsState.ABORTED,
    )
    event_recorder.subscribe_event(central_node_mid.subarray_node, "obsState")
    assert event_recorder.has_change_event_occurred(
        central_node_mid.subarray_node,
        "obsState",
        ObsState.ABORTED,
    )


@when(
    parsers.parse(
        "I issue the Restart command on TMC SubarrayNode {subarray_id}"
    )
)
def send_command_restart(central_node_mid):
    central_node_mid.subarray_node.Restart()


@then(
    parsers.parse(
        "the CSP, SDP and TMC subarray {subarray_id} transitions to "
        + "obsState EMPTY"
    )
)
def subarray_transitions_to_empty(
    central_node_mid, simulator_factory, event_recorder
):
    csp_sim, sdp_sim, _, _, _, _ = get_device_simulators(simulator_factory)
    event_recorder.subscribe_event(csp_sim, "obsState")
    assert event_recorder.has_change_event_occurred(
        csp_sim,
        "obsState",
        ObsState.EMPTY,
    )
    event_recorder.subscribe_event(sdp_sim, "obsState")
    assert event_recorder.has_change_event_occurred(
        sdp_sim,
        "obsState",
        ObsState.EMPTY,
    )
    event_recorder.subscribe_event(central_node_mid.subarray_node, "obsState")
    assert event_recorder.has_change_event_occurred(
        central_node_mid.subarray_node,
        "obsState",
        ObsState.EMPTY,
    )


@then(
    parsers.parse(
        "AssignResources command is executed successfully on the "
        + "Subarray {subarray_id}"
    )
)
def assign_resources_executed_on_subarray(
    central_node_mid, event_recorder, command_input_factory
):
    event_recorder.subscribe_event(central_node_mid.subarray_node, "obsState")
    event_recorder.subscribe_event(
        central_node_mid.central_node, "longRunningCommandResult"
    )
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_mid", command_input_factory
    )

    _, unique_id = central_node_mid.perform_action(
        "AssignResources", assign_input_json
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.subarray_node,
        "obsState",
        ObsState.IDLE,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "longRunningCommandResult",
        (unique_id[0], Anything),
    )
