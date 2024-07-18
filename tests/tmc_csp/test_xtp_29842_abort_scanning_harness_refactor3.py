"""Test TMC-CSP Abort functionality in Scanning obstate"""
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
    "../features/tmc_csp/xtp_29842_abort_scanning.feature",
    "Abort scanning CSP using TMC",
)
def test_tmc_csp_abort_in_scanning_refactor3():
    """Test case to verify TMC-CSP Abort functionality in SCANNING obsState"""


@given("the telescope is in ON state")
def telescope_is_in_on_state(
    central_node_facade: TMCCentralNodeFacade,
):
    """Checks if the telescope is in ON state"""
    central_node_facade.move_to_on(wait_termination_condition=True)


@given(
    parsers.parse(
        "the TMC subarray {subarray_id} and CSP subarray {subarray_id} are "
        + "busy in SCANNING"
    )
)
def subarray_is_in_scanning_obsstate(
    subarray_node_facade: TMCSubarrayNodeFacade,
    csp: CSPFacade,
    tmc_mid_json_factory: IJsonFactory,
    event_tracer: TangoEventTracer,
    subarray_id: str,
):
    """A method to check if subarray is in SCANNING obsState."""
    subarray_node_facade.set_subarray_id(subarray_id)

    assign_input_json = (
        tmc_mid_json_factory.create_central_node_assign_resources_command_input()  # pylint: disable=line-too-long # noqa: E501
    )
    configure_input_json = (
        tmc_mid_json_factory.create_subarray_configure_command_input()
    )
    scan_input_json = tmc_mid_json_factory.create_subarray_scan_command_input()

    subarray_node_facade.force_change_of_obs_state(
        ObsState.SCANNING,
        assign_input_json=assign_input_json,
        configure_input_json=configure_input_json,
        scan_input_json=scan_input_json,
        json_factory=tmc_mid_json_factory,
        wait_termination_condition=True,
    )

    event_tracer.subscribe_event(
        subarray_node_facade.subarray_node, "obsState"
    )
    event_tracer.subscribe_event(csp.csp_subarray, "obsState")
    log_events(
        {
            csp.csp_subarray: ["obsState"],
            subarray_node_facade.subarray_node: ["obsState"],
        }
    )


@when("I issued the Abort command to the TMC subarray")
def abort_is_invoked(
    subarray_node_facade: TMCSubarrayNodeFacade, event_tracer: TangoEventTracer
):
    """This method invokes abort command on TMC subarray."""
    subarray_node_facade.abort(wait_termination_condition=False)

    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION: "
        "TMC Subarray Node device "
        f"({subarray_node_facade.subarray_node}) "
        "Abort command invocation has been performed "
        "after obsState is not anymore SCANNING, "
        "because automatic ScanComplete transaction triggered."
    ).hasnt_change_event_occurred(
        subarray_node_facade.subarray_node,
        "obsState",
        ObsState.READY,
        previous_value=ObsState.SCANNING,
    )


@then("the CSP subarray transitions to ObsState ABORTED")
def csp_subarray_is_in_aborted_obsstate(
    csp: CSPFacade, event_tracer: TangoEventTracer
):
    """Method to check if CSP subarray is in ABORTED obsState"""
    assert_that(event_tracer).described_as(
        "CSP Subarray device "
        f"({csp.csp_subarray}) "
        "ObsState attribute value is supposed to move to ABORTING "
        "and then to ABORTED."
    ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
        csp.csp_subarray,
        "obsState",
        ObsState.ABORTING,
        previous_value=ObsState.SCANNING,
    ).has_change_event_occurred(
        csp.csp_subarray,
        "obsState",
        ObsState.ABORTED,
        previous_value=ObsState.ABORTING,
    )


@then("the TMC subarray transitions to ObsState ABORTED")
def tmc_subarray_is_in_aborted_obsstate(
    subarray_node_facade: TMCSubarrayNodeFacade,
    event_tracer: TangoEventTracer,
):
    """Method to check if TMC subarray is in ABORTED obsState"""
    assert_that(event_tracer).described_as(
        "TMC Subarray Node device "
        f"({subarray_node_facade.subarray_node}) "
        "ObsState attribute value is supposed to move to ABORTING "
        "and then to ABORTED."
    ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
        subarray_node_facade.subarray_node,
        "obsState",
        ObsState.ABORTING,
        previous_value=ObsState.SCANNING,
    ).has_change_event_occurred(
        subarray_node_facade.subarray_node,
        "obsState",
        ObsState.ABORTED,
        previous_value=ObsState.ABORTING,
    )
