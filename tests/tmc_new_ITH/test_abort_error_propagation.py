"""
Test for Abort() error propagation verification
"""
import json

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
from ska_tmc_common import FaultType

from tests.tmc_csp_new_ITH.conftest import (
    ASSERTIONS_TIMEOUT,
    SubarrayTestContextData,
)

ERROR_PROPAGATION_DEFECT = json.dumps(
    {
        "enabled": True,
        "fault_type": FaultType.LONG_RUNNING_EXCEPTION,
        "error_message": "Exception occured, command failed.",
        "result": ResultCode.FAILED,
    }
)


def _setup_event_subscriptions(
    tmc: TMCFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
    event_tracer: TangoEventTracer,
):
    """Subscribe TMC, CSP and SDP devices to track and log obsState events.

    :param tmc: the TMC facade.
    :param csp: the CSP facade.
    :param sdp: the SDP facade.
    :param event_tracer: the event tracer.
    """
    event_tracer.subscribe_event(tmc.subarray_node, "obsState")
    event_tracer.subscribe_event(csp.csp_subarray, "obsState")
    event_tracer.subscribe_event(sdp.sdp_subarray, "obsState")
    event_tracer.subscribe_event(tmc.central_node, "longRunningCommandResult")
    event_tracer.subscribe_event(tmc.subarray_node, "longRunningCommandResult")

    log_events(
        {
            tmc.subarray_node: [
                "obsState",
                "longRunningCommandResult",
            ],
            csp.csp_subarray: ["obsState"],
            sdp.sdp_subarray: ["obsState"],
            tmc.central_node: ["longRunningCommandResult"],
        },
        event_enum_mapping={"obsState": ObsState},
    )


@pytest.mark.batch1
@pytest.mark.SKA_mid
@scenario(
    "../tmc_new_ITH/features/abort_error_propagation.feature",
    "Error Propagation Reported by TMC Mid Abort and Restart Commands for"
    " Defective Subarray",
)
def test_verify_abort_error_propagation():
    """Test for Abort command error propagation."""


@given(
    parsers.parse(
        "the TMC subarray is in the {initialObsState} " "observation state"
    )
)
def subarray_in_ready_state(
    context_fixt: SubarrayTestContextData,
    tmc: TMCFacade,
    sdp: SDPFacade,
    csp: CSPFacade,
    event_tracer: TangoEventTracer,
    default_commands_inputs: TestHarnessInputs,
    initialObsState: ObsState,
):
    """Ensure the subarray is in the initial obsstate state."""
    _setup_event_subscriptions(tmc, csp, sdp, event_tracer)
    context_fixt.starting_state = ObsState.IDLE

    tmc.force_change_of_obs_state(
        ObsState.IDLE,
        default_commands_inputs,
        wait_termination=True,
    )


@when(
    parsers.parse(
        "{command} is invoked on a defectiveSubsystem" " {defectiveSubsystem}"
    )
)
def send_abort_command(
    context_fixt: SubarrayTestContextData,
    tmc: TMCFacade,
    csp: CSPFacade,
    command: str,
):
    """
    Send the Scan command to the subarray.

    This step uses the tmc to send a Scan command to the
    specified subarray. It uses a pre-defined JSON input file and sends
    the command without waiting for termination. The action result is
    stored in the context fixture.
    """
    csp.csp_subarray.SetDefective(ERROR_PROPAGATION_DEFECT)
    context_fixt.when_action_name = command
    context_fixt.when_action_result = tmc.abort()


@then(("the command failure is reported by subarray with error message"))
def verify_error_message(
    context_fixt: SubarrayTestContextData,
    tmc: TMCFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
    event_tracer: TangoEventTracer,
):
    """
    Verify the subarray's transition to the SCANNING state.

    This step checks that the ObsState attribute of the TMC Subarray Node,
    CSP Subarray, and SDP Subarray devices all transition from the starting
    state to the SCANNING state. It uses the event_tracer to assert that these
    state changes occur within a specified timeout. After verification, it
    updates the starting state in the context fixture for subsequent steps.
    """
    assert_that(event_tracer).described_as(
        f"Both TMC Subarray Node device ({tmc.subarray_node})"
        f", CSP Subarray device ({csp.csp_subarray}) "
        f"and SDP Subarray device ({sdp.sdp_subarray}) "
        "ObsState attribute values should move "
        f"from {str(context_fixt.starting_state)} to SCANNING."
    ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
        tmc.subarray_node,
        "obsState",
        ObsState.SCANNING,
        previous_value=context_fixt.starting_state,
    ).has_change_event_occurred(
        csp.csp_subarray,
        "obsState",
        ObsState.SCANNING,
        previous_value=context_fixt.starting_state,
    ).has_change_event_occurred(
        sdp.sdp_subarray,
        "obsState",
        ObsState.SCANNING,
        previous_value=context_fixt.starting_state,
    )

    # override the starting state for the next step
    context_fixt.starting_state = ObsState.SCANNING


@then(parsers.parse("the TMC SubarrayNode remains in {stuck} obsState"))
def verify_ready_state(
    context_fixt: SubarrayTestContextData,
    tmc: TMCFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
    event_tracer: TangoEventTracer,
):
    """
    Verify the subarray's transition to the READY state.

    This step checks that the ObsState attribute of the TMC Subarray Node,
    CSP Subarray, and SDP Subarray devices all transition from the starting
    state to the READY state. It uses the event_tracer to assert that these
    state changes occur within a specified timeout. After verification, it
    updates the starting state in the context fixture for subsequent steps.
    """
    assert_that(event_tracer).described_as(
        f"Both TMC Subarray Node device ({tmc.subarray_node})"
        f", CSP Subarray device ({csp.csp_subarray}) "
        f"and SDP Subarray device ({sdp.sdp_subarray}) "
        "ObsState attribute values should move "
        f"from {str(context_fixt.starting_state)} to READY."
    ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
        tmc.subarray_node,
        "obsState",
        ObsState.READY,
        previous_value=context_fixt.starting_state,
    ).has_change_event_occurred(
        csp.csp_subarray,
        "obsState",
        ObsState.READY,
        previous_value=context_fixt.starting_state,
    ).has_change_event_occurred(
        sdp.sdp_subarray,
        "obsState",
        ObsState.READY,
        previous_value=context_fixt.starting_state,
    )

    # override the starting state for the next step
    context_fixt.starting_state = ObsState.READY
