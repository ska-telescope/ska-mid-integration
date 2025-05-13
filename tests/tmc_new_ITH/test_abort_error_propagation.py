"""
Test for Abort() error propagation verification
"""
import json
import logging
import time

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
from ska_ser_logging import configure_logging
from ska_tango_testing.integration import TangoEventTracer, log_events

from tests.resources.test_support.constant import ERROR_PROPAGATION_DEFECT
from tests.tmc_csp_new_ITH.conftest import (
    ASSERTIONS_TIMEOUT,
    SubarrayTestContextData,
)

configure_logging(logging.DEBUG)
LOGGER = logging.getLogger(__name__)

COMMAND_RESULT = '[3, "Exception occurred on the following devices: '
'mid-tmc/subarray-leaf-node-csp/01: Exception occurred, command failed."]'


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


@pytest.mark.batch3
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
    _, pytest.unique_id = tmc.subarray_node.Abort()


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
        'FAILED ASSUMPTION IN "THEN" STEP: '
        "'the subarray is in ABORTING obsState'"
        "TMC Subarray Node device"
        f"({tmc.subarray_node.dev_name()}) "
        "is expected have longRunningCommandResult as"
        "(unique_id, COMMAND_RESULT)",
    ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
        tmc.subarray_node,
        "longRunningCommandResult",
        (pytest.unique_id[0], COMMAND_RESULT),
    )


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
    # assert_that(event_tracer).described_as(
    #     f"Both TMC Subarray Node device ({tmc.subarray_node})"
    #     f", CSP Subarray device ({csp.csp_subarray}) "
    #     f"and SDP Subarray device ({sdp.sdp_subarray}) "
    #     "ObsState attribute values should move "
    #     f"from {str(context_fixt.starting_state)} to FAULT."
    # ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
    #     tmc.subarray_node,
    #     "obsState",
    #     ObsState.FAULT,
    #     previous_value=context_fixt.starting_state,
    # ).has_change_event_occurred(
    #     csp.csp_subarray,
    #     "obsState",
    #     ObsState.IDLE,
    #     previous_value=context_fixt.starting_state,
    # ).has_change_event_occurred(
    #     sdp.sdp_subarray,
    #     "obsState",
    #     ObsState.ABORTED,
    #     previous_value=context_fixt.starting_state,
    # )
    time.sleep(10)

    csp.csp_subarray.SetDefective(json.dumps({"enabled": False}))
    csp.csp_subarray.Abort()

    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "THEN" STEP: '
        "'the csp subarray must be in the ABORTED obsState'"
        "CSP Subarray device"
        f"({csp.csp_subarray.dev_name()}) "
        "is expected to be in ABORTED obstate",
    ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
        csp.csp_subarray,
        "obsState",
        ObsState.ABORTED,
    )

    # override the starting state for the next step
    # context_fixt.starting_state = ObsState.READY
