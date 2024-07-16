"""Test module for TMC-CSP Scan functionality."""
import pytest
from assertpy import assert_that
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState
from ska_tango_testing.integration import TangoEventTracer, log_events

from tests.test_harness3.common_utils.i_json_factory import IJsonFactory
from tests.test_harness3.telescope_facades.csp_facade import CSPFacade
from tests.test_harness3.telescope_facades.tmc_central_node_facade import (
    TMCCentralNodeFacade,
)
from tests.test_harness3.telescope_facades.tmc_subarray_node_facade import (
    TMCSubarrayNodeFacade,
)

ASSERTIONS_TIMEOUT = 60


@pytest.mark.tmc_csp
@scenario(
    "../features/ai_generated_scenarios.feature",
    "READY to SCANNING CMD Scan - 26",
)
def test_ready_to_scanning_via_scan_ai_generated():
    """Verify subarray transition from READY to SCANNING."""


#
# Scenario: READY to SCANNING CMD Scan - 26
#   Given the subarray 001 is in the READY state
#   When the Scan command is sent to subarray 001
#   Then the subarray 001 should transition to the SCANNING state


def _setup_event_subscriptions(
    subarray_node_facade: TMCSubarrayNodeFacade,
    csp: CSPFacade,
    event_tracer: TangoEventTracer,
):
    """Set up event subscriptions for the test.

    Args:
        subarray_node_facade: Facade for the TMC subarray node.
        csp: Facade for the CSP.
        event_tracer: Event tracer for capturing events.
    """
    event_tracer.subscribe_event(csp.csp_subarray, "obsState")
    event_tracer.subscribe_event(
        subarray_node_facade.subarray_node, "obsState"
    )
    log_events(
        {
            csp.csp_subarray: ["obsState"],
            subarray_node_facade.subarray_node: ["obsState"],
        }
    )


@given(parsers.parse("the subarray {subarray_id} is in the READY state"))
def subarray_in_ready_state(
    tmc_mid_json_factory: IJsonFactory,
    subarray_node_facade: TMCSubarrayNodeFacade,
    central_node_facade: TMCCentralNodeFacade,
    csp: CSPFacade,
    event_tracer: TangoEventTracer,
    subarray_id: str,
):
    """Ensure the telescope is ON and the subarray is in the READY state.

    This step performs the following actions:
    1. Moves the telescope to ON state.
    2. Sets up event subscriptions for the specified subarray.
    3. Sets the subarray ID.
    4. Moves the subarray to READY state.

    Args:
        command_input_factory: Factory for creating command inputs.
        subarray_node_facade: Facade for the TMC subarray node.
        central_node_facade: Facade for the TMC central node.
        csp: Facade for the CSP.
        event_tracer: Event tracer for capturing events.
        subarray_id: ID of the subarray being tested.
    """

    # Move the telescope to ON state
    central_node_facade.move_to_on(
        # wait_termination=True,
        wait_termination_condition=True,
    )

    # Set subarray ID
    subarray_node_facade.set_subarray_id(subarray_id)

    # Move subarray to READY state
    subarray_node_facade.force_change_of_obs_state(
        ObsState.READY,
        # assign_input_json=prepare_json_args_for_centralnode_commands(
        #     "assign_resources_mid", command_input_factory
        # ),
        # configure_input_json=prepare_json_args_for_commands(
        #     "configure_mid", command_input_factory
        # ),
        assign_input_json=tmc_mid_json_factory.create_central_node_assign_resources_command_input(),  # pylint: disable=line-too-long # noqa: E501
        configure_input_json=tmc_mid_json_factory.create_subarray_configure_command_input(),  # pylint: disable=line-too-long # noqa: E501
        json_factory=tmc_mid_json_factory,
        # wait_termination=True,
        wait_termination_condition=True,
    )

    # Set up event subscriptions
    _setup_event_subscriptions(subarray_node_facade, csp, event_tracer)


@when(parsers.parse("the Scan command is sent to subarray {subarray_id}"))
def send_scan_command(
    subarray_node_facade: TMCSubarrayNodeFacade,
    tmc_mid_json_factory: IJsonFactory,
):
    """Send the Scan command to the specified subarray.

    This step prepares the scan input JSON and sends the Scan command
    to the subarray without waiting for termination.

    Args:
        subarray_node_facade: Facade for the TMC subarray node.
        command_input_factory: Factory for creating command inputs.
        subarray_id: ID of the subarray being tested.
    """
    # scan_input_json = prepare_json_args_for_commands(
    #     "scan_mid", command_input_factory
    # )

    scan_input_json = tmc_mid_json_factory.create_subarray_scan_command_input()

    subarray_node_facade.scan(
        scan_input_json,
        # wait_termination=False
        wait_termination_condition=False,
    )


@then(
    parsers.parse(
        "the subarray {subarray_id} should transition to the SCANNING state"
    )
)
def verify_scanning_state(
    subarray_node_facade: TMCSubarrayNodeFacade,
    csp: CSPFacade,
    event_tracer: TangoEventTracer,
):
    """Verify that both TMC and CSP subarrays transition to the SCANNING state.

    This step checks that both the TMC Subarray Node and the CSP Subarray
    devices transition to the SCANNING state within the specified timeout
    period.

    After that the step aborts the scan and waits for the subarrays
    to move to the ABORTED state and eventually sends a RESTART
    command and waits for the subarray to go the EMPTY state.

    Args:
        subarray_node_facade: Facade for the TMC subarray node.
        csp: Facade for the CSP.
        event_tracer: Event tracer for capturing events.
    """
    assert_that(event_tracer).described_as(
        f"Both TMC Subarray Node device ({subarray_node_facade.subarray_node})"
        f" and CSP Subarray device ({csp.csp_subarray}) "
        "ObsState attribute values are supposed "
        "to move from READY to SCANNING."
    ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
        subarray_node_facade.subarray_node,
        "obsState",
        ObsState.SCANNING,
        previous_value=ObsState.READY,
    ).has_change_event_occurred(
        csp.csp_subarray,
        "obsState",
        ObsState.SCANNING,
        previous_value=ObsState.READY,
    )

    # assert_that(event_tracer).described_as(
    #     f"Both TMC Subarray Node device "
    #     "({subarray_node_facade.subarray_node})"
    #     f" and CSP Subarray device ({csp.csp_subarray}) "
    #     "ObsState attribute values are supposed "
    #     "to come back to READY after the scan duration elapsed."
    # ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
    #     subarray_node_facade.subarray_node,
    #     "obsState",
    #     ObsState.READY,
    #     previous_value=ObsState.SCANNING
    # ).has_change_event_occurred(
    #     csp.csp_subarray,
    #     "obsState",
    #     ObsState.READY,
    #     previous_value=ObsState.SCANNING
    # )

    # and here we want the test to stop the scan and wait for
    # the subarrays to move to
    # the ABORTED state and then the EMPTY state
    # subarray_node_facade.abort_scan(subarray_id)
    subarray_node_facade.abort(wait_termination_condition=True)
    subarray_node_facade.restart(wait_termination_condition=True)

    assert_that(event_tracer).described_as(
        f"ASSUMPTION. \n"
        f"TMC Subarray Node device ({subarray_node_facade.subarray_node})"
        f"ObsState attribute value is supposed to be EMPTY."
    ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
        subarray_node_facade.subarray_node,
        "obsState",
        ObsState.ABORTING,
        # previous value may be either READY or SCANNING
        # previous_value=ObsState.READY,
        # previous_value=ObsState.SCANNING,
    ).has_change_event_occurred(
        subarray_node_facade.subarray_node,
        "obsState",
        ObsState.ABORTED,
        previous_value=ObsState.ABORTING,
    ).has_change_event_occurred(
        subarray_node_facade.subarray_node,
        "obsState",
        ObsState.RESTARTING,
        previous_value=ObsState.ABORTED,
    ).has_change_event_occurred(
        subarray_node_facade.subarray_node,
        "obsState",
        ObsState.EMPTY,
        previous_value=ObsState.RESTARTING,
    )

    assert_that(event_tracer).described_as(
        f"ASSUMPTION. \n"
        f"CSP Subarray device ({csp.csp_subarray}) "
        f"ObsState attribute value is supposed to be EMPTY."
    ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
        csp.csp_subarray,
        "obsState",
        ObsState.ABORTING,
        # previous value may be either READY or SCANNING
        # previous_value=ObsState.READY,
        # previous_value=ObsState.SCANNING,
    ).has_change_event_occurred(
        csp.csp_subarray,
        "obsState",
        ObsState.ABORTED,
        previous_value=ObsState.ABORTING,
    ).has_change_event_occurred(
        csp.csp_subarray,
        "obsState",
        ObsState.RESTARTING,
        previous_value=ObsState.ABORTED,
    ).has_change_event_occurred(
        csp.csp_subarray,
        "obsState",
        ObsState.EMPTY,
        previous_value=ObsState.RESTARTING,
    )

    # NOTE: those tests will fail because the actual state passages are:
    # EMPTY -> ABORTING -> ABORTED -> RESTARTING -> EMPTY

    # assert_that(event_tracer).described_as(
    #     f"ASSUMPTION. \n"
    #     f"Both TMC Subarray Node device "
    #       "({subarray_node_facade.subarray_node})"
    #     f" and CSP Subarray device ({csp.csp_subarray}) "
    #     f"ObsState attribute values are supposed to be EMPTY."
    # ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
    #     subarray_node_facade.subarray_node,
    #     "obsState",
    #     ObsState.EMPTY,
    #     previous_value=ObsState.ABORTED
    # ).has_change_event_occurred(
    #     csp.csp_subarray,
    #     "obsState",
    #     ObsState.EMPTY,
    #     previous_value=ObsState.ABORTED
    # )
