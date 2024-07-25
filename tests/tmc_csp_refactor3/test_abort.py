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
from ska_tango_testing.integration import TangoEventTracer

from tests.test_harness3.telescope_facades.csp_facade import CSPFacade
from tests.test_harness3.telescope_facades.sdp_facade import SDPFacade
from tests.test_harness3.telescope_facades.tmc_subarray_node_facade import (
    TMCSubarrayNodeFacade,
)
from tests.test_harness3.telescope_inputs.obs_state_commands_input import (
    ObsStateCommandsInput,
)
from tests.tmc_csp_refactor3.conftest import StateChangesContextData

ASSERTIONS_TIMEOUT = 30

# ------------------------------------------------------------
# Scenario Definition


# @pytest.mark.skip(
#     "It fails because CSP and/or SDP may not actually abort "
#     "but continue with IDLE. NOTE: both CSP and SDP are emulated "
#     "when trying that, so that may be the reason (?)"
# )
@pytest.mark.tmc_csp_refactor3
@scenario(
    "../tmc_csp_refactor3/features/abort_reset.feature",
    "RESOURCING to ABORTING to ABORTED - CMD Abort (12)",
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
    "../tmc_csp_refactor3/features/abort_reset.feature",
    "IDLE to ABORTING to ABORTED - CMD Abort (19)",
)
def test_idle_to_aborting_to_aborted():
    """Test IDLE to ABORTING to ABORTED transitions."""


# NOTE: it works but just because we don't assume anymore SDP
# should transition to ABORTING state, but directly to ABORTED!

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
    "../tmc_csp_refactor3/features/abort_reset.feature",
    "CONFIGURING to ABORTING to ABORTED - CMD Abort (25)",
)
def test_configuring_to_aborting_to_aborted():
    """Test CONFIGURING to ABORTING to ABORTED transitions."""


@pytest.mark.tmc_csp_refactor3
@scenario(
    "../tmc_csp_refactor3/features/abort_reset.feature",
    "READY to ABORTING to ABORTED - CMD Abort (28)",
)
def test_ready_to_aborting_to_aborted():
    """Test READY to ABORTING to ABORTED transitions."""


@pytest.mark.tmc_csp_refactor3
@scenario(
    "../tmc_csp_refactor3/features/abort_reset.feature",
    "SCANNING to ABORTING to ABORTED - CMD Abort (34)",
)
def test_scanning_to_aborting_to_aborted():
    """Test SCANNING to ABORTING to ABORTED transitions."""


@pytest.mark.tmc_csp_refactor3
@scenario(
    "../tmc_csp_refactor3/features/abort_reset.feature",
    "ABORTED to RESTARTING - CMD Restart (40)",
)
def test_aborted_to_restarting():
    """Test ABORTED to RESTARTING transition."""


# ----------------------------------------------------------
# Given Steps


@given(parsers.parse("the subarray 001 is in the RESOURCING state"))
def subarray_in_resourcing_state(
    context_fixt: StateChangesContextData,
    # subarray_id: str,
    subarray_node_facade: TMCSubarrayNodeFacade,
    default_commands_inputs: ObsStateCommandsInput,
):
    """Ensure the subarray is in the RESOURCING state."""
    context_fixt.starting_state = ObsState.RESOURCING
    context_fixt.expected_next_state = ObsState.IDLE

    subarray_node_facade.force_change_of_obs_state(
        ObsState.RESOURCING,
        default_commands_inputs,
        wait_termination=True,
    )


@given(parsers.parse("the subarray 001 is in the IDLE state"))
def subarray_in_idle_state(
    context_fixt: StateChangesContextData,
    # subarray_id: str,
    subarray_node_facade: TMCSubarrayNodeFacade,
    default_commands_inputs: ObsStateCommandsInput,
):
    """Ensure the subarray is in the IDLE state."""
    context_fixt.starting_state = ObsState.IDLE
    context_fixt.expected_next_state = ObsState.IDLE

    subarray_node_facade.force_change_of_obs_state(
        ObsState.IDLE,
        default_commands_inputs,
        wait_termination=True,
    )


@given(parsers.parse("the subarray 001 is in the CONFIGURING state"))
def subarray_in_configuring_state(
    context_fixt: StateChangesContextData,
    # subarray_id: str,
    subarray_node_facade: TMCSubarrayNodeFacade,
    default_commands_inputs: ObsStateCommandsInput,
):
    """Ensure the subarray is in the CONFIGURING state."""
    context_fixt.starting_state = ObsState.CONFIGURING
    context_fixt.expected_next_state = ObsState.READY

    subarray_node_facade.force_change_of_obs_state(
        ObsState.CONFIGURING,
        default_commands_inputs,
        wait_termination=True,
    )


@given(parsers.parse("the subarray 001 is in the READY state"))
def subarray_in_ready_state(
    context_fixt: StateChangesContextData,
    # subarray_id: str,
    subarray_node_facade: TMCSubarrayNodeFacade,
    default_commands_inputs: ObsStateCommandsInput,
):
    """Ensure the subarray is in the READY state."""
    context_fixt.starting_state = ObsState.READY
    context_fixt.expected_next_state = ObsState.READY

    subarray_node_facade.force_change_of_obs_state(
        ObsState.READY,
        default_commands_inputs,
        wait_termination=True,
    )


@given(parsers.parse("the subarray 001 is in the SCANNING state"))
def subarray_in_scanning_state(
    context_fixt: StateChangesContextData,
    # subarray_id: str,
    subarray_node_facade: TMCSubarrayNodeFacade,
    default_commands_inputs: ObsStateCommandsInput,
):
    """Ensure the subarray is in the SCANNING state."""
    context_fixt.starting_state = ObsState.SCANNING
    context_fixt.expected_next_state = ObsState.READY

    subarray_node_facade.force_change_of_obs_state(
        ObsState.SCANNING,
        default_commands_inputs,
        wait_termination=True,
    )


@given(parsers.parse("the subarray 001 is in the ABORTED state"))
def subarray_in_aborted_state(
    context_fixt: StateChangesContextData,
    # subarray_id: str,
    subarray_node_facade: TMCSubarrayNodeFacade,
    default_commands_inputs: ObsStateCommandsInput,
):
    """Ensure the subarray is in the ABORTED state."""
    context_fixt.starting_state = ObsState.ABORTED
    context_fixt.expected_next_state = ObsState.ABORTED

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


@when(parsers.parse("the Abort command is sent to the subarray 001"))
def send_abort_command(
    context_fixt: StateChangesContextData,
    # subarray_id: str,
    subarray_node_facade: TMCSubarrayNodeFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
    event_tracer: TangoEventTracer,
):
    """Send the Abort command to the subarray."""
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
        ).described_as(
            "FAILED ASSUMPTION: "
            "CSP Subarray Node device "
            f"({csp.csp_subarray}) "
            "Abort command invocation has been performed "
            f"after obsState is {context_fixt.starting_state}, "
            "because automatic transaction triggered."
        ).hasnt_change_event_occurred(
            csp.csp_subarray,
            "obsState",
            context_fixt.expected_next_state,
            previous_value=context_fixt.starting_state,
        ).described_as(
            "FAILED ASSUMPTION: "
            "SDP Subarray Node device "
            f"({sdp.sdp_subarray}) "
            "Abort command invocation has been performed "
            f"after obsState is {context_fixt.starting_state}, "
            "because automatic transaction triggered."
        ).hasnt_change_event_occurred(
            sdp.sdp_subarray,
            "obsState",
            context_fixt.expected_next_state,
            previous_value=context_fixt.starting_state,
        )


@when(parsers.parse("the Restart command is sent to the subarray 001"))
def send_restart_command(
    context_fixt,
    # subarray_id: str,
    subarray_node_facade: TMCSubarrayNodeFacade,
):
    """Send the Restart command to the subarray."""
    subarray_node_facade.restart(wait_termination=False)


# ----------------------------------------------------------
# (Common) Then Steps


@then(
    parsers.parse("the subarray 001 should transition to the ABORTING state")
)
def verify_aborting_state(
    context_fixt,
    subarray_node_facade: TMCSubarrayNodeFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
    event_tracer: TangoEventTracer,
):
    """Verify that the subarray transitions to the ABORTING state."""
    assert_that(event_tracer).described_as(
        f"Both TMC Subarray Node device ({subarray_node_facade.subarray_node})"
        f" and CSP Subarray device ({csp.csp_subarray}) "
        "ObsState attribute values should move to ABORTING."
    ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
        subarray_node_facade.subarray_node,
        "obsState",
        ObsState.ABORTING,
        previous_value=context_fixt.starting_state,
    ).has_change_event_occurred(
        csp.csp_subarray,
        "obsState",
        ObsState.ABORTING,
        # previous_value=context_fixt.starting_state,
        # NOTE: if the starting state is transient, the previous value
        # cannot be verified here, because it may have changed to
        # another state in the meantime. But we still want to guarantee
        # ABORTING is reached
    )

    # (TODO: decide what to do with SDP, which we have to remember is emulated)


@then(parsers.parse("the subarray 001 should transition to the ABORTED state"))
def verify_aborted_state(
    context_fixt,
    subarray_node_facade: TMCSubarrayNodeFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
    event_tracer: TangoEventTracer,
):
    """Verify that the subarray transitions to the ABORTED state."""
    assert_that(event_tracer).described_as(
        f"Both TMC Subarray Node device ({subarray_node_facade.subarray_node})"
        f" and CSP Subarray device ({csp.csp_subarray}) "
        "ObsState attribute values should move to ABORTED."
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
    )

    # (TODO: decide what to do with SDP, which we have to remember is emulated)


@then(
    parsers.parse("the subarray 001 should transition to the RESTARTING state")
)
def verify_restarting_state(
    context_fixt,
    subarray_node_facade: TMCSubarrayNodeFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
    event_tracer: TangoEventTracer,
):
    """Verify that the subarray transitions to the RESTARTING state."""
    assert_that(event_tracer).described_as(
        f"Both TMC Subarray Node device ({subarray_node_facade.subarray_node})"
        f" and CSP Subarray device ({csp.csp_subarray}) "
        "ObsState attribute values should move to RESTARTING."
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
    )

    # (TODO: decide what to do with SDP, which we have to remember is emulated)


@then(parsers.parse("the subarray 001 should transition to the EMPTY state"))
def verify_empty_state(
    context_fixt,
    # subarray_id: str,
    subarray_node_facade: TMCSubarrayNodeFacade,
    csp: CSPFacade,
    event_tracer: TangoEventTracer,
):
    """Verify that the subarray transitions to the EMPTY state."""
    assert_that(event_tracer).described_as(
        f"Both TMC Subarray Node device ({subarray_node_facade.subarray_node})"
        f" and CSP Subarray device ({csp.csp_subarray}) "
        "ObsState attribute values should move to EMPTY."
    ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
        subarray_node_facade.subarray_node,
        "obsState",
        ObsState.EMPTY,
        previous_value=ObsState.RESTARTING,
    ).has_change_event_occurred(
        csp.csp_subarray,
        "obsState",
        ObsState.EMPTY,
        previous_value=ObsState.RESTARTING,
    )

    # (TODO: decide what to do with SDP, which we have to remember is emulated)
