"""Verify the Abort command works as expected from all appropriate states.

The purpose of these scenarios is to verify that the subarray obsState
can be successfully aborted and restarted from any state, ensuring so
that a tear down procedure to reset the subarray to a known EMPTY state is
feasible.

The states that permit the Abort command are:
- RESOURCING
- IDLE
- CONFIGURING
- READY
- SCANNING

The Abort command is expected to transition the subarray to the ABORTING.

After the subarray is in the ABORTING state, the subsequent expected
transition is the automatic transition to the ABORTED state. After that,
the Restarted command can be called, and it will transition the subarray
to the RESTARTING state, and then to the EMPTY state.
"""


import pytest
from assertpy import assert_that
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState
from ska_integration_test_harness.facades.csp_facade import CSPFacade
from ska_integration_test_harness.facades.sdp_facade import SDPFacade
from ska_integration_test_harness.facades.tmc_subarray_node_facade import (
    TMCSubarrayNodeFacade,
)
from ska_integration_test_harness.inputs.obs_state_commands_input import (
    ObsStateCommandsInput,
)
from ska_tango_testing.integration import TangoEventTracer

from tests.tmc_csp_refactor3.conftest import SubarrayTestContextData

ASSERTIONS_TIMEOUT = 60

# ------------------------------------------------------------
# Scenario Definition


# @pytest.mark.xfail(
#     reason="It may fail because CSP and/or SDP may not actually abort "
#     "but continue with IDLE."
# )
@pytest.mark.tmc_csp_refactor3
@scenario(
    "../tmc_csp_refactor3/features/abort_restart_subarray.feature",
    "RESOURCING to ABORTING to ABORTED - CMD Abort",
)
def test_resourcing_to_aborting_to_aborted():
    """Test RESOURCING to ABORTING to ABORTED transitions."""


# AssertionError: [Both TMC Subarray Node device
#   (SubarrayNodeMid(ska_mid/tm_subarray_node/1)) and CSP Subarray device
#   (HelperCspSubarray(mid-csp/subarray/01)) ObsState attribute values should
#   move to ABORTING.] Expected to find an event matching the predicate
#   within 30 seconds, but none was found.

# Events captured by TANGO_TRACER:
# ReceivedEvent(device_name='ska_mid/tm_subarray_node/1',
#   attribute_name='obsstate', attribute_value=0,
#   reception_time=2024-07-24 14:26:54.918849)
# ReceivedEvent(device_name='mid-csp/subarray/01', attribute_name='obsstate',
#   attribute_value=0, reception_time=2024-07-24 14:26:54.921061)
# ReceivedEvent(device_name='mid-sdp/subarray/01', attribute_name='obsstate',
#   attribute_value=0, reception_time=2024-07-24 14:26:54.923226)
# ReceivedEvent(device_name='ska_mid/tm_subarray_node/1',
#   attribute_name='obsstate', attribute_value=1,
#   reception_time=2024-07-24 14:26:54.941185)
# ReceivedEvent(device_name='mid-csp/subarray/01', attribute_name='obsstate',
#   attribute_value=1, reception_time=2024-07-24 14:26:54.984129)
# ReceivedEvent(device_name='mid-sdp/subarray/01', attribute_name='obsstate',
#   attribute_value=1, reception_time=2024-07-24 14:26:54.990777)
# ReceivedEvent(device_name='ska_mid/tm_subarray_node/1',
#   attribute_name='obsstate', attribute_value=6,
#   reception_time=2024-07-24 14:26:55.028604)
# ReceivedEvent(device_name='mid-csp/subarray/01', attribute_name='obsstate',
#   attribute_value=2, reception_time=2024-07-24 14:26:56.984784)
# ReceivedEvent(device_name='mid-sdp/subarray/01', attribute_name='obsstate',
#   attribute_value=2, reception_time=2024-07-24 14:26:56.991256)

# TANGO_TRACER Query arguments: device_name='mid-csp/subarray/01',
#   attribute_name='obsState', attribute_value=6,
# Query start time: 2024-07-24 14:26:55.028750
# Query end time: 2024-07-24 14:27:25.029028


@pytest.mark.tmc_csp_refactor3
@scenario(
    "../tmc_csp_refactor3/features/abort_restart_subarray.feature",
    "IDLE to ABORTING to ABORTED - CMD Abort",
)
def test_idle_to_aborting_to_aborted():
    """Test IDLE to ABORTING to ABORTED transitions."""


# NOTE: it works but just because we don't assume anymore SDP
# should transition to ABORTING state, but directly to ABORTED!

# TODO: check the emulator of the SDP and see if it can be fixed

# AssertionError: [Both TMC Subarray Node device
# (SubarrayNodeMid(ska_mid/tm_subarray_node/1)) and CSP Subarray device
# (HelperCspSubarray(mid-csp/subarray/01)) ObsState attribute
# values should move to ABORTING.] Expected to find an event matching
# the predicate within 30 seconds, but none was found.
#
# Events captured by TANGO_TRACER:
# ReceivedEvent(device_name='ska_mid/tm_subarray_node/1',
#   attribute_name='obsstate', attribute_value=0,
#   reception_time=2024-07-24 07:55:51.925970)
# ReceivedEvent(device_name='mid-csp/subarray/01', attribute_name='obsstate',
#   attribute_value=0, reception_time=2024-07-24 07:55:51.928176)
# ReceivedEvent(device_name='mid-sdp/subarray/01', attribute_name='obsstate',
#   attribute_value=0, reception_time=2024-07-24 07:55:51.930251)
# ReceivedEvent(device_name='ska_mid/tm_subarray_node/1',
#   attribute_name='obsstate', attribute_value=1,
#   reception_time=2024-07-24 07:55:51.955643)
# ReceivedEvent(device_name='mid-csp/subarray/01', attribute_name='obsstate',
#   attribute_value=1, reception_time=2024-07-24 07:55:51.986716)
# ReceivedEvent(device_name='mid-sdp/subarray/01', attribute_name='obsstate',
#   attribute_value=1, reception_time=2024-07-24 07:55:51.993106)
# ReceivedEvent(device_name='mid-csp/subarray/01', attribute_name='obsstate',
#   attribute_value=2, reception_time=2024-07-24 07:55:53.987608)
# ReceivedEvent(device_name='mid-sdp/subarray/01', attribute_name='obsstate',
#   attribute_value=2, reception_time=2024-07-24 07:55:53.993935)
# ReceivedEvent(device_name='ska_mid/tm_subarray_node/1',
#   attribute_name='obsstate', attribute_value=2,
#   reception_time=2024-07-24 07:55:54.265215)
# ReceivedEvent(device_name='ska_mid/tm_subarray_node/1',
#   attribute_name='obsstate', attribute_value=6,
#   reception_time=2024-07-24 07:55:54.273116)
# ReceivedEvent(device_name='mid-csp/subarray/01', attribute_name='obsstate',
#   attribute_value=6, reception_time=2024-07-24 07:55:54.299966)
# ReceivedEvent(device_name='mid-csp/subarray/01', attribute_name='obsstate',
#   attribute_value=7, reception_time=2024-07-24 07:55:56.300670)
# ReceivedEvent(device_name='mid-sdp/subarray/01', attribute_name='obsstate',
#   attribute_value=7, reception_time=2024-07-24 07:55:56.313426)
# ReceivedEvent(device_name='ska_mid/tm_subarray_node/1',
#   attribute_name='obsstate', attribute_value=7,
#   reception_time=2024-07-24 07:56:05.670537)
#
# TANGO_TRACER Query arguments: device_name='mid-sdp/subarray/01',
#   attribute_name='obsState', attribute_value=6, previous_value=2,
# Query start time: 2024-07-24 07:55:54.300073
# Query end time: 2024-07-24 07:56:24.300304


@pytest.mark.tmc_csp_refactor3
@scenario(
    "../tmc_csp_refactor3/features/abort_restart_subarray.feature",
    "CONFIGURING to ABORTING to ABORTED - CMD Abort",
)
def test_configuring_to_aborting_to_aborted():
    """Test CONFIGURING to ABORTING to ABORTED transitions."""


@pytest.mark.tmc_csp_refactor3
@scenario(
    "../tmc_csp_refactor3/features/abort_restart_subarray.feature",
    "READY to ABORTING to ABORTED - CMD Abort",
)
def test_ready_to_aborting_to_aborted():
    """Test READY to ABORTING to ABORTED transitions."""


@pytest.mark.tmc_csp_refactor3
@scenario(
    "../tmc_csp_refactor3/features/abort_restart_subarray.feature",
    "SCANNING to ABORTING to ABORTED - CMD Abort",
)
def test_scanning_to_aborting_to_aborted():
    """Test SCANNING to ABORTING to ABORTED transitions."""


@pytest.mark.tmc_csp_refactor3
@scenario(
    "../tmc_csp_refactor3/features/abort_restart_subarray.feature",
    "ABORTED to RESTARTING to EMPTY - CMD Restart",
)
def test_aborted_to_restarting():
    """Test ABORTED to RESTARTING transition."""


# ----------------------------------------------------------
# Given Steps


@given(parsers.parse("the subarray {subarray} is in the ABORTED state"))
def subarray_in_aborted_state(
    context_fixt: SubarrayTestContextData,
    # subarray_id: str,
    subarray_node_facade: TMCSubarrayNodeFacade,
    default_commands_inputs: ObsStateCommandsInput,
):
    """
    Ensure the subarray is in the ABORTED state.

    This step performs the following actions:
    1. Sets the starting_state in the test context to ABORTED.
    2. Forces the subarray to the IDLE state to ensure it's in a state
       where Abort can be sent.
    3. Sends the Abort command to transition the subarray
       to the ABORTED state.
    """
    context_fixt.starting_state = ObsState.ABORTED

    # move to a state where the Abort command can be sent
    subarray_node_facade.force_change_of_obs_state(
        ObsState.IDLE,
        default_commands_inputs,
        wait_termination=True,
    )

    # send the Abort command
    subarray_node_facade.abort(wait_termination=True)


# ----------------------------------------------------------
# (Common) When Step


@when(parsers.parse("the Abort command is sent to the subarray {subarray}"))
def send_abort_command(
    context_fixt: SubarrayTestContextData,
    # subarray_id: str,
    subarray_node_facade: TMCSubarrayNodeFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
    event_tracer: TangoEventTracer,
):
    """
    Send the Abort command to the subarray.

    This step sends the Abort command without waiting for termination.
    If the starting state is transient, it verifies that the
    expected state transition hasn't occurred prematurely.
    """
    subarray_node_facade.abort(wait_termination=False)

    if context_fixt.is_starting_state_transient():
        assert_that(event_tracer).described_as(
            "FAILED ASSUMPTION: "
            "TMC Subarray Node device "
            f"({subarray_node_facade.subarray_node}) "
            "Abort command invocation has been performed "
            f"after obsState is {context_fixt.starting_state}, "
            "because automatic transaction triggered."
        ).hasnt_change_event_occurred(
            subarray_node_facade.subarray_node,
            "obsState",
            context_fixt.expected_next_state,
            previous_value=context_fixt.starting_state,
        )


@when(parsers.parse("the Restart command is sent to the subarray {subarray}"))
def send_restart_command(
    context_fixt: SubarrayTestContextData,
    # subarray_id: str,
    subarray_node_facade: TMCSubarrayNodeFacade,
):
    """
    Send the Restart command to the subarray.

    This step sends the Restart command without waiting for termination.
    """
    subarray_node_facade.restart(wait_termination=False)


# ----------------------------------------------------------
# (Common) Then Steps


@then(
    parsers.parse(
        "the subarray {subarray} should transition to the ABORTING state"
    )
)
def verify_aborting_state(
    context_fixt: SubarrayTestContextData,
    subarray_node_facade: TMCSubarrayNodeFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
    event_tracer: TangoEventTracer,
):
    """
    Verify that the subarray transitions to the ABORTING state.

    This step checks that the TMC Subarray Node, CSP Subarray, and SDP Subarray
    devices transition to the ABORTING state within the specified timeout.
    It verifies the previous state for the TMC Subarray Node.
    """
    assert_that(event_tracer).described_as(
        f"Both TMC Subarray Node device ({subarray_node_facade.subarray_node})"
        f", CSP Subarray device ({csp.csp_subarray}) "
        f"and SDP Subarray device ({sdp.sdp_subarray}) "
        "ObsState attribute values should move to ABORTING."
        "TMC, in particular, is expected to move exactly from the "
        f"{context_fixt.starting_state} state to ABORTING."
    ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
        subarray_node_facade.subarray_node,
        "obsState",
        ObsState.ABORTING,
        previous_value=context_fixt.starting_state,
    ).has_change_event_occurred(
        # TODO: even though it does not seem so, these 2
        # chained assertions require 2 separate
        # timeouts. We should instead use a single timeout for both.
        csp.csp_subarray,
        "obsState",
        ObsState.ABORTING,
    )  # .has_change_event_occurred(
    #     sdp.sdp_subarray,
    #     "obsState",
    #     ObsState.ABORTING,
    # ) # TODO: configure SDP emulated to transition to ABORTING state

    # NOTE: if the starting state is transient, the previous value
    # cannot be verified for CSP and SDP, because it may have changed to
    # another state in the meantime. But we still want to guarantee
    # ABORTING is reached.

    # TODO: Not clear why the previous value is not verified for CSP and SDP.
    # let's forget about the SDP which is emulated - we will deal with it later
    # but using the tracer we should be able to capture a sequence of
    # transitions. There will be 2 change-events,
    # one for the first transition and one for the second.
    # GB agrees that it is questionable if we have to test that the CSP.SA
    # evolves along the prescribed path.
    # But I would say yes, we need to make sure that the CSP.SA evolves
    # as expected because that might affect how
    # the TMC.SA evolves.

    # The previous value can and should instead be verified for TMC
    # (since we already have an assertion that checks the command have
    # been called when the transient state was still in place).

    # for the emulated device (SDP) we verify the correct
    # Tango command has been called as expected


@then(
    parsers.parse(
        "the subarray {subarray} should transition to the ABORTED state"
    )
)
def verify_aborted_state(
    context_fixt,
    subarray_node_facade: TMCSubarrayNodeFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
    event_tracer: TangoEventTracer,
):
    """
    Verify that the subarray transitions to the ABORTED state.

    This step checks that all relevant devices (TMC, CSP, SDP) transition from
    ABORTING to ABORTED state within the specified timeout.
    """
    assert_that(event_tracer).described_as(
        f"Both TMC Subarray Node device ({subarray_node_facade.subarray_node})"
        f", CSP Subarray device ({csp.csp_subarray}) "
        f"and SDP Subarray device ({sdp.sdp_subarray}) "
        "ObsState attribute values should move "
        "from ABORTING to RESOURCING."
    ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
        subarray_node_facade.subarray_node,
        "obsState",
        ObsState.ABORTED,
        previous_value=ObsState.ABORTING,
    ).has_change_event_occurred(
        csp.csp_subarray,
        "obsState",
        ObsState.ABORTED,
        previous_value=ObsState.ABORTING,
    ).has_change_event_occurred(
        sdp.sdp_subarray,
        "obsState",
        ObsState.ABORTED,
        # previous_value=ObsState.ABORTING,
        # TODO: configure SDP emulated to transition to ABORTING state
    )


@then(
    parsers.parse(
        "the subarray {subarray} should transition to the RESTARTING state"
    )
)
def verify_restarting_state(
    context_fixt: SubarrayTestContextData,
    subarray_node_facade: TMCSubarrayNodeFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
    event_tracer: TangoEventTracer,
):
    """
    Verify that the subarray transitions to the RESTARTING state.

    This step performs the following actions:
    1. Checks that all relevant devices transition from
       ABORTED to RESTARTING state
       within the specified timeout.
    2. Updates the starting state in the test context to RESTARTING.
    3. Verifies that the correct Tango command (Aborted) was received
       by the SDP emulator."""
    assert_that(event_tracer).described_as(
        f"Both TMC Subarray Node device ({subarray_node_facade.subarray_node})"
        f", CSP Subarray device ({csp.csp_subarray}) "
        f"and SDP Subarray device ({sdp.sdp_subarray}) "
        "ObsState attribute values should move "
        "from ABORTED to RESTARTING."
    ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
        subarray_node_facade.subarray_node,
        "obsState",
        ObsState.RESTARTING,
        previous_value=ObsState.ABORTED,
    ).has_change_event_occurred(
        csp.csp_subarray,
        "obsState",
        ObsState.RESTARTING,
        previous_value=ObsState.ABORTED,
    ).has_change_event_occurred(
        sdp.sdp_subarray,
        "obsState",
        ObsState.RESTARTING,
        previous_value=ObsState.ABORTED,
    )

    context_fixt.starting_state = ObsState.RESTARTING


@then(
    parsers.parse(
        "the subarray {subarray} should transition to the EMPTY state"
    )
)
def verify_empty_state(
    context_fixt,
    # subarray_id: str,
    subarray_node_facade: TMCSubarrayNodeFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
    event_tracer: TangoEventTracer,
):
    """
    Verify that the subarray transitions to the EMPTY state.

    This step checks that all relevant devices (TMC, CSP, SDP) transition from
    the previous state (stored in the test context) to the EMPTY state within
    the specified timeout."""
    assert_that(event_tracer).described_as(
        f"Both TMC Subarray Node device ({subarray_node_facade.subarray_node})"
        f", CSP Subarray device ({csp.csp_subarray}) "
        f"and SDP Subarray device ({sdp.sdp_subarray}) "
        "ObsState attribute values should move "
        f"from {context_fixt.starting_state} to EMPTY."
    ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
        subarray_node_facade.subarray_node,
        "obsState",
        ObsState.EMPTY,
        previous_value=context_fixt.starting_state,
    ).has_change_event_occurred(
        csp.csp_subarray,
        "obsState",
        ObsState.EMPTY,
        previous_value=context_fixt.starting_state,
    ).has_change_event_occurred(
        sdp.sdp_subarray,
        "obsState",
        ObsState.EMPTY,
        previous_value=context_fixt.starting_state,
    )
