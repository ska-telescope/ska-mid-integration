"""Test case to verify Restart after Assign Resource Fails
"""

import pytest
from assertpy import assert_that
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState
from ska_integration_test_harness.facades.csp_facade import CSPFacade
from ska_integration_test_harness.facades.sdp_facade import SDPFacade
from ska_integration_test_harness.facades.tmc_facade import TMCFacade
from ska_integration_test_harness.inputs.test_harness_inputs import (
    TestHarnessInputs,
)
from ska_tango_base.commands import ResultCode
from ska_tango_testing.integration import TangoEventTracer, log_events
from ska_tango_testing.mock.placeholders import Anything

from tests.tmc_csp_new_ITH.conftest import (
    ASSERTIONS_TIMEOUT,
    SubarrayTestContextData,
)
from tests.tmc_new_ITH.conftest import TestContextData
from tests.tmc_new_ITH.utils.utils import (
    invoke_command_with_defect,
    reset_defects,
    setup_event_subscriptions,
)


def _check_abort_flow(
    csp: CSPFacade,
    sdp: SDPFacade,
    context_data: TestContextData,
    event_tracer: TangoEventTracer,
):
    """This function checks obstates for abort and
    tracks abort flow if it will be aborted.
    """
    abort_not_allowed_obs_states = [
        ObsState.ABORTED,
        ObsState.FAULT,
        ObsState.EMPTY,
    ]
    if context_data.csp_obsstate not in abort_not_allowed_obs_states:
        assert_that(event_tracer).described_as(
            f"CSP Subarray device ({csp.csp_subarray}) "
            "ObsState attribute values should move "
            f"to ABORTED."
        ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
            csp.csp_subarray,
            "obsState",
            ObsState.ABORTED,
            previous_value=ObsState.ABORTING,
        )

    if context_data.sdp_obsstate not in abort_not_allowed_obs_states:
        assert_that(event_tracer).described_as(
            f"SDP Subarray device ({sdp.sdp_subarray}) "
            "ObsState attribute values should move "
            f"to ABORTED."
        ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
            sdp.sdp_subarray,
            "obsState",
            ObsState.ABORTED,
            previous_value=ObsState.ABORTING,
        )


@pytest.mark.batch1_fault
@pytest.mark.SKA_mid
@scenario(
    "../tmc_new_ITH/features/xtp_82859_fault_assign_scan.feature",
    "Test Restart Command during failure of AssignResources and Scan Command",
)
def test_verify_fault_after_assign_or_scan():
    """Test Restart command behaviour after Assign or Scan command fails"""


@given(
    parsers.parse(
        "CSP and SDP in observation states {csp_obsstate} and {sdp_obsstate} "
        "after {command}"
    )
)
def subarray_in_idle_state(
    context_fixt: SubarrayTestContextData,
    tmc: TMCFacade,
    sdp: SDPFacade,
    csp: CSPFacade,
    event_tracer: TangoEventTracer,
    default_commands_inputs: TestHarnessInputs,
    csp_obsstate,
    sdp_obsstate,
    command,
    context_data: TestContextData,
):
    """Ensure the subarray is in the IDLE state."""
    setup_event_subscriptions(tmc, csp, sdp, event_tracer)
    invoke_command_with_defect(
        tmc,
        default_commands_inputs,
        csp,
        sdp,
        csp_obsstate,
        sdp_obsstate,
        command,
    )
    assert_that(event_tracer).described_as(
        f"CSP Subarray device ({csp.csp_subarray})"
        "ObsState attribute value should move "
        f"to {csp_obsstate}."
    ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
        csp.csp_subarray, "obsState", ObsState[csp_obsstate]
    )

    assert_that(event_tracer).described_as(
        f"SDP Subarray device ({sdp.sdp_subarray})"
        "ObsState attribute value should move "
        f" to {sdp_obsstate}."
    ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
        sdp.sdp_subarray, "obsState", ObsState[sdp_obsstate]
    )
    context_data.csp_obsstate = ObsState[csp_obsstate]
    context_data.sdp_obsstate = ObsState[sdp_obsstate]


@given("TMC Subarray in observation state FAULT")
def verify_tmc_subarray_observation_state_fault(
    event_tracer: TangoEventTracer,
    tmc: TMCFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
):
    """Verifies the TMC subarray observation state FAULT"""
    assert_that(event_tracer).described_as(
        f"TMC Subarray Node device ({tmc.subarray_node})"
        "ObsState attribute value should move "
        f" to FAULT."
    ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
        tmc.subarray_node,
        "obsState",
        ObsState.FAULT,
    )

    log_events({tmc.subarray_node: ["longRunningCommandResult"]})

    assert_that(event_tracer).described_as(
        f"FAILED ASSUMPTION: "
        "Subarray Node device"
        f"({tmc.subarray_node}) "
        "is expected to have longRunningCommandResult"
        "(ResultCode.FAILED,Timeout has occurred, command failed)",
    ).within_timeout(
        ASSERTIONS_TIMEOUT
    ).has_desired_result_code_message_in_lrcr_event(
        tmc.subarray_node,
        ["occurred"],
        Anything,
        ResultCode.FAILED,
    )

    reset_defects(csp, sdp)


@when("I invoke restart command on the TMC Subarray")
def invoke_restart_command(tmc: TMCFacade):
    """Invokes restart command on the TMC Subarray."""
    tmc.restart()


@then("CSP and SDP transitions to observation state EMPTY")
def verify_sdp_csp_mccs_in_empty_observation_state(
    event_tracer: TangoEventTracer,
    csp: CSPFacade,
    sdp: SDPFacade,
    context_data: TestContextData,
):
    """Verifies the observation states of SDP,CSP and MCCS
    after command Restart.
    """
    _check_abort_flow(csp, sdp, context_data, event_tracer)
    (
        assert_that(event_tracer)
        .described_as(
            f", CSP Subarray device ({csp.csp_subarray}) "
            f"and SDP Subarray device ({sdp.sdp_subarray}) "
            "ObsState attribute values should move "
            f"to RESTARTING."
        )
        .within_timeout(ASSERTIONS_TIMEOUT)
        .has_change_event_occurred(
            csp.csp_subarray, "obsState", ObsState.RESTARTING
        )
        .has_change_event_occurred(
            sdp.sdp_subarray, "obsState", ObsState.RESTARTING
        )
    )

    assert_that(event_tracer).described_as(
        f", CSP Subarray device ({csp.csp_subarray}) "
        f"and SDP Subarray device ({sdp.sdp_subarray}) "
        "ObsState attribute values should move "
        f"to EMPTY."
    ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
        csp.csp_subarray, "obsState", ObsState.EMPTY
    ).has_change_event_occurred(
        sdp.sdp_subarray, "obsState", ObsState.EMPTY
    )


@then("TMC subarray transitions to observation state EMPTY")
def verify_tmc_subarray_in_empty_observation_state(
    event_tracer: TangoEventTracer, tmc: TMCFacade
):
    """Verifies the observation state of TMC Subarray."""
    assert_that(event_tracer).described_as(
        f"TMC Subarray Node device ({tmc.subarray_node})"
        "ObsState attribute value should move "
        f"from {ObsState.FAULT} to EMPTY."
    ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
        tmc.subarray_node, "obsState", ObsState.EMPTY
    )
