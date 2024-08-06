"""Test NonSidereal tracking for TMC"""
import json

import pytest
from assertpy import assert_that
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState, ResultCode
from ska_tango_testing.integration import TangoEventTracer, log_events
from tango import DevState

from tests.resources.test_harness.central_node_mid import CentralNodeWrapperMid
from tests.resources.test_harness.helpers import (
    LOGGER,
    get_non_sidereal_json_for_now,
    prepare_json_args_for_centralnode_commands,
)
from tests.resources.test_harness.subarray_node import SubarrayNodeWrapper
from tests.resources.test_harness.utils.common_utils import JsonFactory

# Assertion timeouts
TIMEOUT = 50
PROGRAM_TRACK_TABLE_LENGTH = 75


@pytest.mark.SKA_mid
@scenario(
    "../features/test_harness/xtp_59647_non_sidereal_tracking.feature",
    "Non sidereal tracking in TMC",
)
def test_non_sidereal_tracking():
    """
    Test writing of programTrackTable for Non-sidereal tracking
    """


@given("a Subarray with resources assigned")
def subarray_with_resources(
    central_node_mid: CentralNodeWrapperMid,
    event_tracer: TangoEventTracer,
    command_input_factory: JsonFactory,
):
    """A subarray that has resources assigned"""
    # Setting up subscriptions
    event_tracer.subscribe_event(
        central_node_mid.central_node, "telescopeState"
    )
    event_tracer.subscribe_event(
        central_node_mid.central_node, "longRunningCommandResult"
    )
    event_tracer.subscribe_event(central_node_mid.subarray_node, "obsState")

    # Logging setup
    log_events(
        {
            central_node_mid.central_node: [
                "telescopeState",
                "longRunningCommandResult",
            ],
            central_node_mid.subarray_node: ["obsState"],
        }
    )

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
            json.dumps((int(ResultCode.OK), "Command Completed")),
        ),
    )


@when(
    parsers.parse(
        "I Configure it for tracking a non-sidereal object from "
        + "{non_sidereal_objects}"
    )
)
def configure_the_subarray(
    non_sidereal_objects: str,
    subarray_node: SubarrayNodeWrapper,
):
    """When subarray is configured"""
    # Configure for Non-sidereal Tracking
    # If a source is visible within elevation limits, run the configure
    # command, else skip.
    object_list = non_sidereal_objects.split(",")
    configure_input_json, object_name = get_non_sidereal_json_for_now()
    pytest.OBJECT_NAME = object_name
    if configure_input_json:
        assert object_name in object_list
        LOGGER.info(
            "The non-sidereal object visible right now for the Dish SKA001"
            + " is: %s",
            object_name,
        )
        subarray_node.store_configuration_data(configure_input_json)


@then("the Subarray is configured successfully")
def subarray_that_is_configured(
    subarray_node: SubarrayNodeWrapper,
    event_tracer: TangoEventTracer,
):
    """A configured subarray"""
    if pytest.OBJECT_NAME:
        # Assertions for Configure
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
    else:
        LOGGER.info("No source is visible within Elevation limits right now")


@then("the dish is tracking the object")
def dish_that_is_tracking(
    central_node_mid: CentralNodeWrapperMid,
):
    """A configured subarray"""
    if pytest.OBJECT_NAME:
        programTrackTable = central_node_mid.get_track_table_for_dish_id(
            "SKA001"
        )
        LOGGER.info("Value for programTrackTable is: %s", programTrackTable)
        assert len(programTrackTable) == PROGRAM_TRACK_TABLE_LENGTH
    else:
        LOGGER.info("No source is visible within Elevation limits right now")
