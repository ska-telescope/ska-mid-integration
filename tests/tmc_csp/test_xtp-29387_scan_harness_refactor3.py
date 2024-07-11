"""Test module for TMC-CSP Scan functionality"""
import pytest
from assertpy import assert_that
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState
from ska_tango_testing.integration import TangoEventTracer, log_events
from tango import DevState

from tests.test_harness2.helpers import (
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
)
from tests.test_harness3.telescope_facades.csp_facade import CSPFacade
from tests.test_harness3.telescope_facades.tmc_central_node_facade import (
    TMCCentralNodeFacade,
)
from tests.test_harness3.telescope_facades.tmc_subarray_node_facade import (
    TMCSubarrayNodeFacade,
)
from tests.test_harness3.utils.common_utils import JsonFactory

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
    csp: CSPFacade,
    event_tracer: TangoEventTracer,
):
    """Checks if CentralNode's telescopeState attribute value is on."""
    event_tracer.subscribe_event(
        central_node_facade.central_node, "telescopeState"
    )
    event_tracer.subscribe_event(csp.csp_master, "State")
    event_tracer.subscribe_event(csp.csp_subarray, "State")

    log_events(
        {
            central_node_facade.central_node: ["telescopeState"],
            csp.csp_master: ["State"],
            csp.csp_subarray: ["State"],
        }
    )

    # central_node_facade.csp_master.adminMode = 0
    # wait_csp_master_off()
    central_node_facade.move_to_on(wait_termination_condition=True)

    # assert_that(event_tracer).described_as(
    #     "FAILED ASSERTION IN 'GIVEN' STEP: "
    #     "CSP Master device "
    #     f"({csp.csp_master}) "
    #     "State attribute value is supposed to be ON."
    # ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
    #     csp.csp_master,
    #     "State",
    #     DevState.ON,
    # )
    # assert_that(event_tracer).described_as(
    #     "FAILED ASSERTION IN 'GIVEN' STEP: "
    #     "CSP Subarray device "
    #     f"({csp.csp_subarray}) "
    #     "State attribute value is supposed to be ON."
    # ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
    #     csp.csp_subarray,
    #     "State",
    #     DevState.ON,
    # )
    # assert_that(event_tracer).described_as(
    #     "FAILED ASSERTION IN 'GIVEN' STEP: "
    #     "TMC Central Node device "
    #     f"({central_node_facade.central_node}) "
    #     "telescopeState attribute value is supposed to be ON."
    # ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
    #     central_node_facade.central_node,
    #     "telescopeState",
    #     DevState.ON,
    # )


@given(parsers.parse("TMC subarray {subarray_id} is in READY ObsState"))
def subarray_in_ready_obsstate(
    event_tracer: TangoEventTracer,
    command_input_factory: JsonFactory,
    subarray_node_facade: TMCSubarrayNodeFacade,
    csp: CSPFacade,
    subarray_id: str,
) -> None:
    """Move TMC Subarray to READY obsstate."""
    subarray_node_facade.set_subarray_id(subarray_id)

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

    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_mid", command_input_factory
    )
    configure_input_json = prepare_json_args_for_commands(
        "configure_mid", command_input_factory
    )
    subarray_node_facade.force_change_of_obs_state(
        ObsState.READY,
        assign_input_json=assign_input_json,
        configure_input_json=configure_input_json,
        wait_termination_condition=True,
    )

    # assert_that(event_tracer).described_as(
    #     "FAILED ASSERTION IN 'GIVEN' STEP: "
    #     "CSP Subarray device "
    #     f"({csp.csp_subarray}) "
    #     "ObsState attribute value is supposed to be READY."
    # ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
    #     csp.csp_subarray,
    #     "obsState",
    #     ObsState.READY,
    # )
    # assert_that(event_tracer).described_as(
    #     "FAILED ASSERTION IN 'GIVEN' STEP: "
    #     "TMC Subarray Node device "
    #     f"({subarray_node_facade.subarray_node}) "
    #     "ObsState attribute value is supposed to be READY."
    # ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
    #     subarray_node_facade.subarray_node,
    #     "obsState",
    #     ObsState.READY,
    # )


@when(
    parsers.parse("I issue the scan command to the TMC subarray {subarray_id}")
)
def invoke_scan(
    subarray_node_facade: TMCSubarrayNodeFacade,
    command_input_factory,
):
    """Invokes Scan command on TMC"""
    scan_input_json = prepare_json_args_for_commands(
        "scan_mid", command_input_factory
    )
    subarray_node_facade.scan(
        scan_input_json, 
        wait_termination_condition=False
    )
    # assert False


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
    subarray_node_facade: TMCSubarrayNodeFacade,
    csp: CSPFacade,
    event_tracer,
    subarray_id,
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
