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
from tests.tmc_csp_refactor3.conftest import TRANSIENT_STATES

ASSERTIONS_TIMEOUT = 30

# ------------------------------------------------------------
# Scenario Definition


@pytest.mark.skip(
    "It fails because of failed assumption, the Abort command is sent "
    "when the subarray already passed the transient state. "
    "The inconsistent state then makes fail the teardown procedure "
    "(TMC-SDP leaf doesn't reach the expected EMPTY state)."
)
@pytest.mark.tmc_csp_refactor3
@scenario(
    "../tmc_csp_refactor3/features/abort_reset.feature",
    "RESOURCING to ABORTING to ABORTED - CMD Abort (12)",
)
def test_resourcing_to_aborting_to_aborted():
    """Test RESOURCING to ABORTING to ABORTED transitions."""


@pytest.mark.skip(
    reason="It fails because SDP (emulated) does not transition "
    "IDLE -> ABORTING -> ABORTED, "
    "but instead it passes directly IDLE -> ABORTED."
)
@pytest.mark.tmc_csp_refactor3
@scenario(
    "../tmc_csp_refactor3/features/abort_reset.feature",
    "IDLE to ABORTING to ABORTED - CMD Abort (19)",
)
def test_idle_to_aborting_to_aborted():
    """Test IDLE to ABORTING to ABORTED transitions."""


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


@pytest.mark.skip(
    "It fails because of failed assumption, the Abort command is sent "
    "when the subarray already passed the transient state. "
    "The inconsistent state then makes fail the teardown procedure "
    "(TMC subarray is ABORTING so it doesn't execute the Reset operation)."
)
@pytest.mark.tmc_csp_refactor3
@scenario(
    "../tmc_csp_refactor3/features/abort_reset.feature",
    "CONFIGURING to ABORTING to ABORTED - CMD Abort (25)",
)
def test_configuring_to_aborting_to_aborted():
    """Test CONFIGURING to ABORTING to ABORTED transitions."""


@pytest.mark.skip(
    reason="It fails because SDP (emulated) does not transition "
    "READY -> ABORTING -> ABORTED, "
    "but instead it passes directly READY -> ABORTED."
)
@pytest.mark.tmc_csp_refactor3
@scenario(
    "../tmc_csp_refactor3/features/abort_reset.feature",
    "READY to ABORTING to ABORTED - CMD Abort (28)",
)
def test_ready_to_aborting_to_aborted():
    """Test READY to ABORTING to ABORTED transitions."""


@pytest.mark.skip(
    "It fails because of failed assumption, the Abort command is sent "
    "when the subarray already passed the transient state. "
    "The inconsistent state then makes fail the teardown procedure "
    "(TMC subarray is ABORTING so it doesn't execute the Reset operation)."
)
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
    context_fixt,
    # subarray_id: str,
    subarray_node_facade: TMCSubarrayNodeFacade,
    default_commands_inputs: ObsStateCommandsInput,
):
    """Ensure the subarray is in the RESOURCING state."""
    context_fixt["starting_state"] = ObsState.RESOURCING
    subarray_node_facade.force_change_of_obs_state(
        ObsState.RESOURCING,
        default_commands_inputs,
        wait_termination=True,
    )


@given(parsers.parse("the subarray 001 is in the IDLE state"))
def subarray_in_idle_state(
    context_fixt,
    # subarray_id: str,
    subarray_node_facade: TMCSubarrayNodeFacade,
    default_commands_inputs: ObsStateCommandsInput,
):
    """Ensure the subarray is in the IDLE state."""
    context_fixt["starting_state"] = ObsState.IDLE
    subarray_node_facade.force_change_of_obs_state(
        ObsState.IDLE,
        default_commands_inputs,
        wait_termination=True,
    )


@given(parsers.parse("the subarray 001 is in the CONFIGURING state"))
def subarray_in_configuring_state(
    context_fixt,
    # subarray_id: str,
    subarray_node_facade: TMCSubarrayNodeFacade,
    default_commands_inputs: ObsStateCommandsInput,
):
    """Ensure the subarray is in the CONFIGURING state."""
    context_fixt["starting_state"] = ObsState.CONFIGURING
    """Ensure the subarray is in the CONFIGURING state."""
    subarray_node_facade.force_change_of_obs_state(
        ObsState.CONFIGURING,
        default_commands_inputs,
        wait_termination=True,
    )


@given(parsers.parse("the subarray 001 is in the READY state"))
def subarray_in_ready_state(
    context_fixt,
    # subarray_id: str,
    subarray_node_facade: TMCSubarrayNodeFacade,
    default_commands_inputs: ObsStateCommandsInput,
):
    """Ensure the subarray is in the READY state."""
    context_fixt["starting_state"] = ObsState.READY
    subarray_node_facade.force_change_of_obs_state(
        ObsState.READY,
        default_commands_inputs,
        wait_termination=True,
    )


@given(parsers.parse("the subarray 001 is in the SCANNING state"))
def subarray_in_scanning_state(
    context_fixt,
    # subarray_id: str,
    subarray_node_facade: TMCSubarrayNodeFacade,
    default_commands_inputs: ObsStateCommandsInput,
):
    """Ensure the subarray is in the SCANNING state."""

    context_fixt["starting_state"] = ObsState.SCANNING
    subarray_node_facade.force_change_of_obs_state(
        ObsState.SCANNING,
        default_commands_inputs,
        wait_termination=True,
    )


@given(parsers.parse("the subarray 001 is in the ABORTED state"))
def subarray_in_aborted_state(
    context_fixt,
    # subarray_id: str,
    subarray_node_facade: TMCSubarrayNodeFacade,
    default_commands_inputs: ObsStateCommandsInput,
):
    """Ensure the subarray is in the ABORTED state."""
    context_fixt["starting_state"] = ObsState.ABORTED

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
    context_fixt,
    # subarray_id: str,
    subarray_node_facade: TMCSubarrayNodeFacade,
    event_tracer: TangoEventTracer,
):
    """Send the Abort command to the subarray."""
    context_fixt["trigger"] = "Abort"
    """Send the Abort command to the subarray."""

    starting_state = context_fixt["starting_state"]
    subarray_node_facade.abort(wait_termination=False)

    if starting_state in TRANSIENT_STATES:
        assert_that(event_tracer).described_as(
            "FAILED ASSUMPTION: "
            "TMC Subarray Node device "
            f"({subarray_node_facade.subarray_node}) "
            "Abort command invocation has been performed "
            f"after obsState is {starting_state}, "
            "because automatic transaction triggered."
        ).hasnt_change_event_occurred(
            subarray_node_facade.subarray_node,
            "obsState",
            ObsState.ABORTING,
            previous_value=starting_state,
        )


@when(parsers.parse("the Restart command is sent to the subarray 001"))
def send_restart_command(
    context_fixt,
    # subarray_id: str,
    subarray_node_facade: TMCSubarrayNodeFacade,
):
    """Send the Restart command to the subarray."""
    context_fixt["trigger"] = "Restart"
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
        previous_value=context_fixt["starting_state"],
    ).has_change_event_occurred(
        csp.csp_subarray,
        "obsState",
        ObsState.ABORTING,
        previous_value=context_fixt["starting_state"],
    ).has_change_event_occurred(
        sdp.sdp_subarray,
        "obsState",
        ObsState.ABORTING,
        previous_value=context_fixt["starting_state"],
    )

    context_fixt["starting_state"] = ObsState.ABORTING


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
        previous_value=context_fixt["starting_state"],
    ).has_change_event_occurred(
        csp.csp_subarray,
        "obsState",
        ObsState.ABORTED,
        previous_value=context_fixt["starting_state"],
    ).has_change_event_occurred(
        sdp.sdp_subarray,
        "obsState",
        ObsState.ABORTED,
        previous_value=context_fixt["starting_state"],
    )

    context_fixt["starting_state"] = ObsState.ABORTED


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
        previous_value=context_fixt["starting_state"],
    ).has_change_event_occurred(
        csp.csp_subarray,
        "obsState",
        ObsState.RESTARTING,
        previous_value=context_fixt["starting_state"],
    ).has_change_event_occurred(
        sdp.sdp_subarray,
        "obsState",
        ObsState.RESTARTING,
        previous_value=context_fixt["starting_state"],
    )

    context_fixt["starting_state"] = ObsState.RESTARTING


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
        previous_value=context_fixt["starting_state"],
    ).has_change_event_occurred(
        csp.csp_subarray,
        "obsState",
        ObsState.EMPTY,
        previous_value=context_fixt["starting_state"],
    )

    context_fixt["starting_state"] = ObsState.EMPTY
