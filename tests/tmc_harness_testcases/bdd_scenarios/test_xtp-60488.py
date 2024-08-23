"""Test case to verify TMC Behavior during correction key handling."""

import json

import pytest
from assertpy import assert_that
from numpy import array_equal
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState
from ska_tango_testing.integration import TangoEventTracer, log_events
from tango import DevState

from tests.resources.test_harness.central_node_mid import CentralNodeWrapperMid
from tests.resources.test_harness.constant import COMMAND_COMPLETED
from tests.resources.test_harness.helpers import (
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
)
from tests.resources.test_harness.subarray_node import SubarrayNodeWrapper
from tests.resources.test_harness.utils.common_utils import JsonFactory
from tests.resources.test_harness.utils.enums import SimulatorDeviceType

# Assertion timeouts
TIMEOUT = 110


@pytest.mark.SKA_mid
@scenario(
    "../features/test_harness/xtp-60488_dish_correction_maintain_key.feature",
    "TMC Behavior During correction key handling",
)
def test_tmc_dish_configure_with_maintain_correction_key():
    """
    Test case to verify TMC Behavior during correction key handling
    on a TMC subarray.
    """


@given("a TMC")
def given_tmc(
    central_node_mid: CentralNodeWrapperMid,
    subarray_node: SubarrayNodeWrapper,
    event_tracer: TangoEventTracer,
):
    """Given a TMC setup for the test."""
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

    for dish_master in subarray_node.dish_master_list:
        event_tracer.subscribe_event(dish_master, "dishMode")

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


@when(
    parsers.parse(
        "five point calibration scan performed on given subarray using "
        "correction key {correction_key}"
    )
)
def a_subarray_after_five_point_calibration(
    central_node_mid: CentralNodeWrapperMid,
    subarray_node: SubarrayNodeWrapper,
    event_tracer: TangoEventTracer,
    simulator_factory,
    command_input_factory: JsonFactory,
    correction_key,
):
    """When a five-point calibration scan is performed on a subarray using
    the given correction key."""
    sdp_sim = simulator_factory.get_or_create_simulator_device(
        SimulatorDeviceType.MID_SDP_DEVICE
    )
    # AssignResources
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_mid", command_input_factory
    )
    _, unique_id = central_node_mid.store_resources(assign_input_json)
    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION AFTER ASSIGNRESOURCES COMMAND: "
        "Subarray Node device"
        f"({central_node_mid.subarray_node.dev_name()}) "
        "is expected to be in IDLE obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_mid.subarray_node,
        "obsState",
        ObsState.IDLE,
    )
    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION AFTER ASSIGNRESOURCES COMMAND: "
        "'the subarray is in IDLE obsState'"
        "Subarray Node device"
        f"({central_node_mid.central_node.dev_name()}) "
        "is expected have longRunningCommand as"
        '(unique_id,(ResultCode.OK,"Command Completed"))',
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_mid.central_node,
        "longRunningCommandResult",
        (
            unique_id[0],
            COMMAND_COMPLETED,
        ),
    )
    subarray_node.simulate_receive_addresses_event(
        sdp_sim, command_input_factory
    )
    event_tracer.clear_events()

    # Configure command
    configure_input_json = prepare_json_args_for_commands(
        "configure_mid", command_input_factory
    )
    # Update the configuration with the correction key
    configure_data = json.loads(configure_input_json)
    configure_data["pointing"]["correction"] = correction_key
    configure_input_str = json.dumps(configure_data)

    pytest.existed_offset = subarray_node.dish_leaf_node_list[0].sourceOffset

    _, unique_id = subarray_node.execute_transition(
        "Configure", configure_input_str
    )

    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION AFTER CONFIGURE COMMAND: "
        "Subarray Node device"
        f"({subarray_node.subarray_node.dev_name()}) "
        "is expected to be in READY obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.READY,
    )
    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION AFTER CONFIGURE COMMAND: "
        "'the subarray is in READY obsState'"
        "Subarray Node device"
        f"({subarray_node.subarray_node.dev_name()}) "
        "is expected have longRunningCommand as"
        '(unique_id,(ResultCode.OK,"Command Completed"))',
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node.subarray_node,
        "longRunningCommandResult",
        (
            unique_id[0],
            COMMAND_COMPLETED,
        ),
    )

    # Partial configurations for Configure command
    partial_configure_json = prepare_json_args_for_commands(
        "partial_configure_1", command_input_factory
    )

    _, unique_id = subarray_node.execute_transition(
        "Configure", partial_configure_json
    )
    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION AFTER CONFIGURE COMMAND: "
        "Subarray Node device"
        f"({subarray_node.subarray_node.dev_name()}) "
        "is expected to be in READY obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.READY,
    )
    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION AFTER CONFIGURE COMMAND: "
        "'the subarray is in READY obsState'"
        "Subarray Node device"
        f"({subarray_node.subarray_node.dev_name()}) "
        "is expected have longRunningCommand as"
        '(unique_id,(ResultCode.OK,"Command Completed"))',
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node.subarray_node,
        "longRunningCommandResult",
        (
            unique_id[0],
            COMMAND_COMPLETED,
        ),
    )
    # Setting pointing calibration data
    subarray_node.set_pointing_cal_on_queue_connector()

    event_tracer.clear_events()


@then(
    "the dish leaf node receive correction key from SDP and " + "reset"
    " all the Dishes"
)
def subarray_applies_calibration_solutions_to_dishes(
    subarray_node: SubarrayNodeWrapper,
):
    """Then the dish leaf node fetches and applies the calibration
    solutions to the dishes."""
    assert array_equal(
        pytest.existed_offset,
        subarray_node.dish_leaf_node_list[0].sourceOffset,
    )
