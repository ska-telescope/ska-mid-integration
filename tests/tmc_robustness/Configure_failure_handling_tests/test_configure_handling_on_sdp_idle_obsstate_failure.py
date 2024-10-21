import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState
from tango import DevState

from tests.resources.test_harness.helpers import (
    get_device_simulators,
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
)
from tests.resources.test_harness.utils.enums import SimulatorDeviceType


@pytest.mark.SKA_mid
@scenario(
    "../features/xtp-28835.feature",
    "TMC behavior when SDP Subarray Configure raises exception",
)
def test_configure_handling_on_sdp_subarray_obsstate_idle_failure():
    """
    Test to verify TMC failure handling when Configure command fails on
    SDP Subarray. Configure completes on CSP Subarray and
    it transitions to obsState READY.
    Whereas SDP Subarray raises exception and transitions
    to obsState IDLE. As a handling End is invoked on CSP Subarray.
    CSP Subarray then moves to obsState IDLE.
    SubarrayNode aggregates obsStates of the lower Subarrays
    and transitions to obsState IDLE.
    """


@given("a TMC")
def given_tmc(central_node_mid, subarray_node, event_recorder):
    event_recorder.subscribe_event(
        central_node_mid.central_node, "telescopeState"
    )
    event_recorder.subscribe_event(subarray_node.subarray_node, "obsState")
    event_recorder.subscribe_event(
        subarray_node.subarray_devices["csp_subarray"], "obsState"
    )
    event_recorder.subscribe_event(
        subarray_node.subarray_devices["sdp_subarray"], "obsState"
    )
    central_node_mid.move_to_on()
    assert event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "telescopeState",
        DevState.ON,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.EMPTY,
    )


@given(parsers.parse("the resources are assigned to TMC SubarrayNode"))
def given_tmc_subarray_assign_resources(
    central_node_mid,
    subarray_node,
    event_recorder,
    simulator_factory,
    command_input_factory,
):
    _, sdp_sim, _, _, _, _ = get_device_simulators(simulator_factory)
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_mid", command_input_factory
    )
    invalid_receiptor_json = prepare_json_args_for_commands(
        "invalid_receiver_address2", command_input_factory
    )
    _, _ = central_node_mid.perform_action(
        "AssignResources", assign_input_json
    )
    sdp_sim.SetDirectreceiveAddresses(invalid_receiptor_json)

    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_devices["csp_subarray"],
        "obsState",
        ObsState.IDLE,
    )

    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_devices["sdp_subarray"],
        "obsState",
        ObsState.IDLE,
    )

    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.IDLE,
    )


@given(
    parsers.parse(
        "the TMC SubarrayNode {subarray_id} Configure is in progress"
    )
)
def given_tmc_subarray_configure_is_in_progress(
    subarray_node, event_recorder, command_input_factory
):
    configure_input_json = prepare_json_args_for_commands(
        "configure_with_invalid_scan_type", command_input_factory
    )
    pytest.command_result = subarray_node.execute_transition(
        "Configure", configure_input_json
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.CONFIGURING,
    )


@given(parsers.parse("Csp Subarray {subarray_id} completes Configure"))
def csp_subarray_configure_complete(event_recorder, simulator_factory):
    csp_sim = simulator_factory.get_or_create_simulator_device(
        SimulatorDeviceType.MID_CSP_DEVICE
    )
    event_recorder.subscribe_event(csp_sim, "obsState")
    assert event_recorder.has_change_event_occurred(
        csp_sim,
        "obsState",
        ObsState.READY,
    )


@given(
    parsers.parse(
        "Sdp Subarray {subarray_id} raises exception and goes back to "
        + "obsState IDLE"
    )
)
def sdp_subarray_returns_to_obsstate_idle(event_recorder, simulator_factory):
    sdp_sim = simulator_factory.get_or_create_simulator_device(
        SimulatorDeviceType.MID_SDP_DEVICE
    )
    event_recorder.subscribe_event(sdp_sim, "obsState")
    assert event_recorder.has_change_event_occurred(
        sdp_sim,
        "obsState",
        ObsState.IDLE,
    )


@given(
    parsers.parse("the TMC SubarrayNode {subarray_id} stucks in CONFIGURING")
)
def given_tmc_subarray_stuck_configuring(
    subarray_node,
):
    assert subarray_node.subarray_node.obsState == ObsState.CONFIGURING


@when(
    parsers.parse(
        "I issue the Abort command on TMC SubarrayNode {subarray_id}"
    )
)
def send_command_abort(subarray_node, event_recorder):
    subarray_node.execute_transition("Abort", argin=None)
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.ABORTING,
    )


@then(
    parsers.parse(
        "the SDP subarray {subarray_id} transitions to obsState ABORTED"
    )
)
def sdp_subarray_transitions_to_aborted(simulator_factory, event_recorder):
    sdp_sim = simulator_factory.get_or_create_simulator_device(
        SimulatorDeviceType.MID_SDP_DEVICE
    )
    assert event_recorder.has_change_event_occurred(
        sdp_sim,
        "obsState",
        ObsState.ABORTED,
    )


@then(
    parsers.parse(
        "the CSP subarray {subarray_id} transitions to obsState ABORTED"
    )
)
def csp_subarray_transitions_to_aborted(simulator_factory, event_recorder):
    csp_sim = simulator_factory.get_or_create_simulator_device(
        SimulatorDeviceType.MID_CSP_DEVICE
    )
    assert event_recorder.has_change_event_occurred(
        csp_sim,
        "obsState",
        ObsState.ABORTED,
    )


@then(
    parsers.parse(
        "Tmc SubarrayNode {subarray_id} transitions to obsState ABORTED"
    )
)
def tmc_subarray_transitions_to_aborted(subarray_node, event_recorder):
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.ABORTED,
        lookahead=18,
    )


@when(
    parsers.parse(
        "I issue the Restart command on TMC SubarrayNode {subarray_id}"
    )
)
def send_command_restart(subarray_node, event_recorder):
    subarray_node.execute_transition("Restart", argin=None)
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.RESTARTING,
    )


@then(
    parsers.parse(
        "the SDP subarray {subarray_id} transitions to obsState EMPTY"
    )
)
def sdp_subarray_transitions_to_empty(simulator_factory, event_recorder):
    sdp_sim = simulator_factory.get_or_create_simulator_device(
        SimulatorDeviceType.MID_SDP_DEVICE
    )
    assert event_recorder.has_change_event_occurred(
        sdp_sim,
        "obsState",
        ObsState.EMPTY,
    )


@then(
    parsers.parse(
        "the CSP subarray {subarray_id} transitions to obsState EMPTY"
    )
)
def csp_subarray_transitions_to_empty(simulator_factory, event_recorder):
    csp_sim = simulator_factory.get_or_create_simulator_device(
        SimulatorDeviceType.MID_CSP_DEVICE
    )
    assert event_recorder.has_change_event_occurred(
        csp_sim,
        "obsState",
        ObsState.EMPTY,
    )


@then(
    parsers.parse(
        "Tmc SubarrayNode {subarray_id} transitions to obsState EMPTY"
    )
)
def tmc_subarray_transitions_to_empty(subarray_node, event_recorder):
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.EMPTY,
    )


@then(
    parsers.parse(
        "Configure command is executed successfully on the "
        + "Subarray {subarray_id}"
    )
)
def configure_executed_on_subarray(
    central_node_mid,
    simulator_factory,
    subarray_node,
    event_recorder,
    command_input_factory,
):
    sdp_sim = simulator_factory.get_or_create_simulator_device(
        SimulatorDeviceType.MID_SDP_DEVICE
    )
    valid_receiptor_json = prepare_json_args_for_commands(
        "science_A_receiver_address", command_input_factory
    )
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_mid", command_input_factory
    )
    sdp_sim.SetDirectreceiveAddresses(valid_receiptor_json)
    central_node_mid.perform_action("AssignResources", assign_input_json)

    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_devices["csp_subarray"],
        "obsState",
        ObsState.IDLE,
    )

    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_devices["sdp_subarray"],
        "obsState",
        ObsState.IDLE,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.subarray_node,
        "obsState",
        ObsState.IDLE,
    )
    configure_input_json = prepare_json_args_for_commands(
        "configure_mid", command_input_factory
    )
    subarray_node.store_configuration_data(configure_input_json)

    # assert event_recorder.has_change_event_occurred(
    #     subarray_node.subarray_devices["csp_subarray"],
    #     "obsState",
    #     ObsState.READY,
    # )
    #
    # assert event_recorder.has_change_event_occurred(
    #     subarray_node.subarray_devices["sdp_subarray"],
    #     "obsState",
    #     ObsState.READY,
    # )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.READY,
    )
