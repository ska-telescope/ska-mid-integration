import json
import time

import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState
from ska_tango_testing.mock.placeholders import Anything
from tango import DevState

from tests.conftest import LOGGER
from tests.resources.test_harness.constant import (
    COMMAND_FAILED_WITH_EXCEPTION_OBSSTATE_IDLE,
)
from tests.resources.test_harness.helpers import (
    get_device_simulators,
    prepare_json_args_for_centralnode_commands,
)


@pytest.mark.SKA_mid
@scenario(
    "../features/xtp-29011.feature",
    "TMC behavior when CSP and SDP Subarrays"
    " incremental AssignResources raise exception",
)
def test_incremental_assign_resources_csp_sdp_subarray_failure(
    central_node_mid, subarray_node, event_recorder, simulator_factory
):
    """
    Test to verify TMC failure handling when incremental AssignResources
    command fails on both CSP and SDP Subarrays.
    CSP and SDP Subarrays raise exception and transitions
    to obsState EMPTY. SubarrayNode aggregates obsStates of the lower Subarrays
    and transitions to obsState EMPTY.
    Glossary:
    - "central_node_mid": fixture for a TMC CentralNode Mid under test
    which provides simulated master devices
    - "event_recorder": fixture for a MockTangoEventCallbackGroup
    for validating the subscribing and receiving events.
    - "simulator_factory": fixture for creating simulator devices for
    mid-Telescope respectively.
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
        "AssignResources is executed successfully"
        " on SubarrayNode {subarray_id} with {input_json1}"
    )
)
def given_assign_resources_executed_on_tmc_subarray(
    central_node_mid,
    event_recorder,
    simulator_factory,
    input_json1,
    command_input_factory,
):
    event_recorder.subscribe_event(central_node_mid.subarray_node, "obsState")

    assign_input_json = prepare_json_args_for_centralnode_commands(
        input_json1, command_input_factory
    )

    central_node_mid.perform_action("AssignResources", assign_input_json)
    assert event_recorder.has_change_event_occurred(
        central_node_mid.subarray_node,
        "obsState",
        ObsState.IDLE,
    )
    time.sleep(0.5)


@given(
    parsers.parse(
        "the next TMC SubarrayNode {subarray_id}"
        " AssignResources is in progress with {input_json2}"
    )
)
def given_tmc_subarray_incremental_assign_resources_is_in_progress(
    central_node_mid,
    event_recorder,
    simulator_factory,
    input_json2,
    command_input_factory,
):
    csp_sim, sdp_sim, _, _, _, _ = get_device_simulators(simulator_factory)
    event_recorder.subscribe_event(csp_sim, "obsState")
    event_recorder.subscribe_event(sdp_sim, "obsState")
    event_recorder.subscribe_event(central_node_mid.subarray_node, "obsState")

    # After AssignResources invocation, CSP Subarray first transtions to
    # obsState RESOURCING and then to the obsState EMPTY due to fault injection
    csp_sim.SetDefective(
        json.dumps(COMMAND_FAILED_WITH_EXCEPTION_OBSSTATE_IDLE)
    )

    # Induce fault on SDP Subarray so that it raises exception and
    # returns to the obsState IDLE
    assign_input_json = prepare_json_args_for_centralnode_commands(
        input_json2, command_input_factory
    )
    central_node_mid.perform_action("AssignResources", assign_input_json)
    assert event_recorder.has_change_event_occurred(
        csp_sim,
        "obsState",
        ObsState.RESOURCING,
    )
    assert event_recorder.has_change_event_occurred(
        sdp_sim,
        "obsState",
        ObsState.RESOURCING,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.subarray_node,
        "obsState",
        ObsState.RESOURCING,
    )


@given(
    parsers.parse(
        "Csp Subarray {subarray_id} raises exception and returns to obsState "
        + "IDLE"
    )
)
def csp_subarray_returns_to_obsstate_idle(event_recorder, simulator_factory):
    csp_sim, _, _, _, _, _ = get_device_simulators(simulator_factory)
    event_recorder.subscribe_event(csp_sim, "obsState")
    assert event_recorder.has_change_event_occurred(
        csp_sim,
        "obsState",
        ObsState.IDLE,
    )


@given(
    parsers.parse(
        "Sdp Subarray {subarray_id} raises exception and returns to obsState "
        + "IDLE"
    )
)
def sdp_subarray_returns_to_obsstate_idle(event_recorder, simulator_factory):
    _, sdp_sim, _, _, _, _ = get_device_simulators(simulator_factory)
    event_recorder.subscribe_event(sdp_sim, "obsState")
    assert event_recorder.has_change_event_occurred(
        sdp_sim,
        "obsState",
        ObsState.IDLE,
    )


@given(
    parsers.parse("the TMC SubarrayNode {subarray_id} stucks in RESOURCING")
)
def given_tmc_subarray_stuck_resourcing(
    central_node_mid, event_recorder, simulator_factory
):
    event_recorder.subscribe_event(central_node_mid.subarray_node, "obsState")
    event_recorder.subscribe_event(
        central_node_mid.subarray_node, "longRunningCommandResult"
    )
    LOGGER.info(
        "SubarrayNode ObsState is %s", central_node_mid.subarray_node.obsState
    )
    assert central_node_mid.subarray_node.obsState == ObsState.RESOURCING
    assert event_recorder.has_change_event_occurred(
        central_node_mid.subarray_node,
        "longRunningCommandResult",
        Anything,
    )
    csp_sim, _, _, _, _, _ = get_device_simulators(simulator_factory)
    csp_sim.SetDefective(json.dumps({"enabled": False}))


@when(
    parsers.parse(
        "I issue the command ReleaseAllResources on SDP and CSP Subarray "
        + "{subarray_id}"
    )
)
def send_command_release(simulator_factory):
    csp_sim, sdp_sim, _, _, _, _ = get_device_simulators(simulator_factory)
    sdp_sim.ReleaseAllResources()
    csp_sim.ReleaseAllResources()


@then(
    parsers.parse(
        "Tmc SubarrayNode {subarray_id} transitions to obsState EMPTY"
    )
)
def tmc_subarray_transitions_to_empty(central_node_mid, event_recorder):
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
