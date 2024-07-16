"""Test module for TMC-CSP Scan functionality"""
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
    central_node_facade.move_to_on(wait_termination_condition=True)


@given(parsers.parse("TMC subarray {subarray_id} is in READY ObsState"))
def subarray_in_ready_obsstate(
    subarray_node_facade: TMCSubarrayNodeFacade,
    tmc_mid_json_factory: IJsonFactory,
    subarray_id: str,
) -> None:
    """Move TMC Subarray to READY obsstate."""
    subarray_node_facade.set_subarray_id(subarray_id)

    # assign_input_json = prepare_json_args_for_centralnode_commands(
    #     "assign_resources_mid", command_input_factory
    # )
    # configure_input_json = prepare_json_args_for_commands(
    #     "configure_mid", command_input_factory
    # )

    assign_input_json = (
        tmc_mid_json_factory.create_central_node_assign_resources_command_input()  # pylint: disable=line-too-long # noqa: E501
    )
    configure_input_json = (
        tmc_mid_json_factory.create_subarray_configure_command_input()
    )

    subarray_node_facade.force_change_of_obs_state(
        ObsState.READY,
        assign_input_json=assign_input_json,
        configure_input_json=configure_input_json,
        json_factory=tmc_mid_json_factory,
        wait_termination_condition=True,
    )


@when(
    parsers.parse("I issue the scan command to the TMC subarray {subarray_id}")
)
def invoke_scan(
    subarray_node_facade: TMCSubarrayNodeFacade,
    csp: CSPFacade,
    event_tracer: TangoEventTracer,
    tmc_mid_json_factory: IJsonFactory,
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

    # scan_input_json = prepare_json_args_for_commands(
    #     "scan_mid", command_input_factory
    # )
    scan_input_json = tmc_mid_json_factory.create_subarray_scan_command_input()
    subarray_node_facade.scan(
        scan_input_json, wait_termination_condition=False
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
