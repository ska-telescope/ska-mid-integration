"""Testing the 5 point calibration scan"""
import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState

from tests.resources.test_harness.helpers import (
    check_subarray_obs_state,
    get_device_simulators,
    prepare_json_args_for_commands,
)


@pytest.mark.SKA_mid
@scenario(
    "../features/test_harness/five_point_scan.feature",
    "TMC behaviour during five point calibration scan.",
)
def test_five_point_calibration_scan():
    """
    Test case to verify the 5 point calibration scan functionality on TMC
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


@given("a subarray configured for a calibration scan")
def a_configured_subarray(
    subarray_node, event_recorder, simulator_factory, command_input_factory
):
    """Given a subarray configured for a calibration scan."""
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


@given("the subarray is in READY obsState")
def a_subarray_in_ready_obsstate():
    """A subarray in READY obsState."""
    assert check_subarray_obs_state("READY", 500)


@when(
    parsers.parse(
        "I perform four partial configurations with json "
        + "{partial_configuration_json} and scans"
    )
)
def when_i_perform_partial_configurations_and_scans(
    subarray_node,
    event_recorder,
    command_input_factory,
    partial_configuration_json,
):
    """When I perform partial configurations and scans."""
    scan_jsons = ["scan_mid" for _ in range(4)]
    partial_configuration_jsons = partial_configuration_json.rstrip().split(
        ","
    )

    subarray_node.execute_five_point_calibration_scan(
        partial_configuration_jsons,
        scan_jsons,
        event_recorder,
        command_input_factory,
    )

    # Check the actual pointing attribute is not empty
    assert subarray_node.dish_leaf_node_list[0].actualPointing


@then(
    "the subarray executes the commands successfully and is in READY obsState"
)
def subarray_executes_commands_successfully():
    """Subarray executes the commands successfully and is in READY obsState."""
    assert check_subarray_obs_state("READY", 500)
