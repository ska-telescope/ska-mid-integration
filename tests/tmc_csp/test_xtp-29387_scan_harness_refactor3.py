# pylint: skip-file
# flake8: noqa

"""Test module for TMC-CSP Scan functionality"""
import pytest
from assertpy import assert_that
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState
from ska_tango_testing.integration import TangoEventTracer, log_events

from tests.various_utils.file_json_input import FileJSONInput

ASSERTIONS_TIMEOUT = 60


@pytest.mark.skip("Redundant test")
@pytest.mark.tmc_csp
@scenario(
    "../features/tmc_csp/xtp_29387_scan.feature",
    "TMC executes a Scan command on CSP subarray.",
)
def test_scan_command_harness_refactor3():
    """BDD test scenario for verifying successful execution of
    the Scan command with TMC and CSP devices for pairwise
    testing."""


@given("the telescope is in ON state")
def given_a_telescope_in_on_state(
    central_node_facade: TMCCentralNodeFacade,
):
    """Checks if CentralNode's telescopeState attribute value is on."""
    central_node_facade.move_to_on(wait_termination=True)


@given(parsers.parse("TMC subarray {subarray_id} is in READY ObsState"))
def subarray_in_ready_obsstate(
    subarray_node_facade: TMCSubarrayNodeFacade,
    default_commands_inputs: ObsStateCommandsInput,
    subarray_id: str,
) -> None:
    """Move TMC Subarray to READY obsstate."""
    subarray_node_facade.set_subarray_id(subarray_id)

    subarray_node_facade.force_change_of_obs_state(
        ObsState.READY,
        commands_inputs=default_commands_inputs,
        wait_termination=True,
    )


@when(
    parsers.parse("I issue the scan command to the TMC subarray {subarray_id}")
)
def invoke_scan(
    subarray_node_facade: TMCSubarrayNodeFacade,
    csp: CSPFacade,
    event_tracer: TangoEventTracer,
):
    """Invokes Scan command on TMC"""
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
    subarray_node_facade.scan(
        FileJSONInput("subarray", "scan_mid"), wait_termination=False
    )


@then(parsers.parse("the CSP subarray transitions to ObsState SCANNING"))
def csp_subarray_scanning(csp: CSPFacade, event_tracer):
    """Checks if Csp Subarray's obsState attribute value is SCANNING"""
    assert_that(event_tracer).described_as(
        "CSP Subarray device "
        f"({csp.csp_subarray}) "
        "ObsState attribute value is supposed to be SCANNING."
    ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
        csp.csp_subarray,
        "obsState",
        ObsState.SCANNING,
    )


@then(
    parsers.parse(
        "the TMC subarray {subarray_id} transitions to ObsState SCANNING"
    )
)
def tmc_subarray_scanning(
    subarray_node_facade: TMCSubarrayNodeFacade,
    event_tracer,
):
    """Checks if SubarrayNode's obsState attribute value is SCANNING"""
    assert_that(event_tracer).described_as(
        "TMC Subarray Node device "
        f"({subarray_node_facade.subarray_node}) "
        "ObsState attribute value is supposed to be SCANNING."
    ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
        subarray_node_facade.subarray_node,
        "obsState",
        ObsState.SCANNING,
    )


@then(
    parsers.parse(
        "the CSP subarray ObsState transitions to READY after the"
        + " scan duration elapsed"
    )
)
def csp_subarray_ObsState(
    csp: CSPFacade,
    event_tracer,
):
    """Checks if SubarrayNode's obsState attribute value is READY"""
    assert_that(event_tracer).described_as(
        "CSP Subarray device "
        f"({csp.csp_subarray}) "
        "ObsState attribute value is supposed to be READY."
    ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
        csp.csp_subarray,
        "obsState",
        ObsState.READY,
    )


@then(
    parsers.parse(
        "the TMC subarray {subarray_id} ObsState transitions back to READY"
    )
)
def tmc_subarray_ready(
    subarray_node_facade: TMCSubarrayNodeFacade,
    event_tracer,
):
    """Checks if SubarrayNode's obsState attribute value is EMPTY"""
    assert_that(event_tracer).described_as(
        "TMC Subarray Node device "
        f"({subarray_node_facade.subarray_node}) "
        "ObsState attribute value is supposed to be READY."
    ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
        subarray_node_facade.subarray_node,
        "obsState",
        ObsState.READY,
    )
