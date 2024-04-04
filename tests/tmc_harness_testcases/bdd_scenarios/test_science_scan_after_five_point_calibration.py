"""Testing the Science Scan after a five point calibration scan"""
import pytest
from pytest_bdd import given, scenario, then, when
from ska_control_model import ObsState
from ska_tango_base.commands import ResultCode

from tests.resources.test_harness.helpers import (
    check_lrcr_events,
    check_subarray_obs_state,
    get_device_simulators,
    prepare_json_args_for_commands,
)
from tests.resources.test_harness.utils.enums import SimulatorDeviceType


@pytest.mark.skip(reason="Fails in READY transition")
@pytest.mark.SKA_mid
@scenario(
    "../features/test_harness/science_scan_after_calibration_scan.feature",
    "TMC behaviour during a science scan after a five point calibration scan.",
)
def test_science_scan_after_five_point_calibration_scan():
    """
    Test case to verify the Science scan functionality after a five point
    calibration scan on TMC
    """


@given("a TMC")
def given_tmc(subarray_node, event_recorder):
    """Given a TMC"""
    event_recorder.subscribe_event(subarray_node.subarray_node, "obsState")
    subarray_node.move_to_on()
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.EMPTY,
    )


@given("a subarray post five point calibration")
def a_subarray_after_five_point_calibration(
    subarray_node, event_recorder, simulator_factory, command_input_factory
):
    """Given a Subarray after the five point Calibration scan."""
    csp_sim, sdp_sim, _, _, _, _ = get_device_simulators(simulator_factory)

    event_recorder.subscribe_event(csp_sim, "obsState")
    event_recorder.subscribe_event(sdp_sim, "obsState")
    event_recorder.subscribe_event(subarray_node.subarray_node, "obsState")
    subarray_node.force_change_of_obs_state("READY")
    assert event_recorder.has_change_event_occurred(
        csp_sim,
        "obsState",
        ObsState.READY,
    )
    assert event_recorder.has_change_event_occurred(
        sdp_sim,
        "obsState",
        ObsState.READY,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.READY,
    )

    scan_command_input = prepare_json_args_for_commands(
        "scan_mid", command_input_factory
    )
    subarray_node.execute_transition("Scan", scan_command_input)
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.SCANNING,
        lookahead=15,
    )
    assert check_subarray_obs_state("READY", 500)

    scan_jsons = ["scan_mid" for _ in range(4)]
    partial_configuration_jsons = [
        f"partial_configure_{i}" for i in range(1, 5)
    ]

    subarray_node.execute_five_point_calibration_scan(
        partial_configuration_jsons,
        scan_jsons,
        event_recorder,
        command_input_factory,
    )


@when("I invoke Configure command for a science scan")
def configure_for_science_scan(
    subarray_node, simulator_factory, command_input_factory
):
    """When Configure is invoked for a Science Scan."""
    configure_command_input = prepare_json_args_for_commands(
        "configure_mid", command_input_factory
    )
    subarray_node.execute_transition("Configure", configure_command_input)
    sdp_sim = simulator_factory.get_or_create_simulator_device(
        SimulatorDeviceType.MID_SDP_DEVICE
    )
    subarray_node.simulate_receive_addresses_event(
        sdp_sim, command_input_factory
    )


@then(
    "the subarray fetches calibration solutions from SDP and applies them to "
    + "the Dishes"
)
def subarray_applies_calibration_solutions_to_dishes(
    subarray_node, event_recorder
):
    """Then the Subarray fetches and applies the configuration solutions to the
    dishes."""
    for dish_leaf_node in subarray_node.dish_leaf_node_list:
        event_recorder.subscribe_event(
            dish_leaf_node, "longRunningCommandResult"
        )

    for dish_leaf_node in subarray_node.dish_leaf_node_list:
        check_lrcr_events(
            event_recorder, dish_leaf_node, "TrackLoadStaticOff", ResultCode.OK
        )


@then("is in READY obsState")
def subarray_is_in_ready_obsstate():
    """Subarray is in READY obsState."""
    assert check_subarray_obs_state("READY", 500)
