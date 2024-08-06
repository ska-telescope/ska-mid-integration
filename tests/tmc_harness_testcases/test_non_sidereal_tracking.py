"""Test Timeout for Configure command for SDP, CSP and MCCS Leaf Nodes."""
# Test to review
import json

import pytest
from assertpy import assert_that
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


class TestNonSiderealTracking:
    """Test for NonSidereal tracking in TMC."""

    @pytest.mark.SKA_mid
    def test_non_sidereal_tracking(
        self,
        central_node_mid: CentralNodeWrapperMid,
        subarray_node: SubarrayNodeWrapper,
        event_tracer: TangoEventTracer,
        command_input_factory: JsonFactory,
    ):
        """Test writing of programTrackTable for Non-sidereal tracking"""
        # Setting up subscriptions
        event_tracer.subscribe_event(
            central_node_mid.central_node, "telescopeState"
        )
        event_tracer.subscribe_event(
            central_node_mid.central_node, "longRunningCommandResult"
        )
        event_tracer.subscribe_event(
            central_node_mid.subarray_node, "obsState"
        )

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

        # Configure for Non-sidereal Tracking
        # If a source is visible within elevation limits, run the configure
        # command, else skip.
        configure_input_json = get_non_sidereal_json_for_now()
        if configure_input_json:
            subarray_node.store_configuration_data(configure_input_json)

            # Assertions for Configure
            assert_that(event_tracer).described_as(
                "FAILED ASSUMPTION AFTER CONFIGURE COMMAND: "
                "Subarray Node device"
                f"({central_node_mid.subarray_node.dev_name()}) "
                "is expected to be in READY obstate",
            ).within_timeout(TIMEOUT).has_change_event_occurred(
                central_node_mid.subarray_node,
                "obsState",
                ObsState.READY,
            )

            programTrackTable = central_node_mid.get_track_table_for_dish_id(
                "SKA001"
            )
            LOGGER.info(
                "Value for programTrackTable is: %s", programTrackTable
            )
            assert len(programTrackTable) == PROGRAM_TRACK_TABLE_LENGTH
        else:
            LOGGER.info(
                "No source is visible within Elevation limits right now"
            )
