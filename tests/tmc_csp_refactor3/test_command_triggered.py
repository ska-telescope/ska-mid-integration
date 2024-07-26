"""The TMC-CSP sub-arrays execute the transition from EMPTY to RESOURCING."""


import pytest
from assertpy import assert_that
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState, ResultCode
from ska_tango_testing.integration import TangoEventTracer

from tests.test_harness3.telescope_facades.csp_facade import CSPFacade
from tests.test_harness3.telescope_facades.sdp_facade import SDPFacade
from tests.test_harness3.telescope_facades.tmc_central_node_facade import (
    TMCCentralNodeFacade,
)
from tests.test_harness3.telescope_facades.tmc_subarray_node_facade import (
    TMCSubarrayNodeFacade,
)
from tests.test_harness3.telescope_inputs.obs_state_commands_input import (
    ObsStateCommandsInput,
)
from tests.tmc_csp_refactor3.conftest import SubarrayTestContextData
from tests.tmc_csp_refactor3.utils.verify_command_call import (
    verify_device_received_command,
)
from tests.various_utils.file_json_input import FileJSONInput

ASSERTIONS_TIMEOUT = 30

# ------------------------------------------------------------
# Scenario


@pytest.mark.tmc_csp_refactor3
@scenario(
    "../tmc_csp_refactor3/features/command_triggered.feature",
    "EMPTY to RESOURCING to IDLE - CMD AssignResources (6)",
)
def test_empty_to_resourcing_to_idle():
    """Test EMPTY to RESOURCING to IDLE transitions."""


@pytest.mark.xfail(
    reason="Without a time.sleep after the telescope reached the IDLE state, "
    "the test fails. But the test should pass without the time.sleep "
    "since if a subarray is in IDLE state, by design it should be able "
    "to receive the Configure command."
)
@pytest.mark.tmc_csp_refactor3
@scenario(
    "../tmc_csp_refactor3/features/command_triggered.feature",
    "IDLE to CONFIGURING to READY - CMD Configure (16)",
)
def test_idle_to_configuring_to_ready():
    """Test IDLE to CONFIGURING to READY transitions."""


@pytest.mark.skip(reason="Not implemented yet.")
@pytest.mark.tmc_csp_refactor3
@scenario(
    "../tmc_csp_refactor3/features/command_triggered.feature",
    "IDLE to RESOURCING to IDLE - CMD AssignResources (18)",
)
def test_idle_to_resourcing_to_idle():
    """Test IDLE to RESOURCING to IDLE transitions."""


@pytest.mark.skip(reason="Not implemented yed.")
@pytest.mark.tmc_csp_refactor3
@scenario(
    "../tmc_csp_refactor3/features/command_triggered.feature",
    "IDLE to RESOURCING to EMPTY - CMD ReleaseResources (17)",
)
def test_idle_to_resourcing_to_empty():
    """Test IDLE to RESOURCING to EMPTY transitions."""


# ------------------------------------------------------------
# Given steps


# The initial common Given steps are already defined in conftest.py


@given(parsers.parse("the subarray {subarray} is in the EMPTY state"))
def subarray_in_empty_state(
    context_fixt: SubarrayTestContextData,
    subarray_node_facade: TMCSubarrayNodeFacade,
):
    """Ensure the subarray is in the EMPTY state."""
    context_fixt.starting_state = ObsState.EMPTY

    subarray_node_facade.force_change_of_obs_state(
        ObsState.EMPTY,
        ObsStateCommandsInput(),
        wait_termination=True,
    )


# ------------------------------------------------------------
# When steps


@when(
    parsers.parse(
        "the AssignResources command is sent to the subarray {subarray}"
    )
)
def send_assign_resources_command(
    context_fixt: SubarrayTestContextData,
    central_node_facade: TMCCentralNodeFacade,
):
    """Send the AssignResources command to the subarray."""
    context_fixt.when_action_name = "AssignResources"

    json_input = FileJSONInput("centralnode", "assign_resources_mid")
    json_input = json_input.set_attribute_value("subarray_id", 1)

    context_fixt.when_action_result = central_node_facade.assign_resources(
        json_input,
        wait_termination=True,
    )


@when(
    parsers.parse(
        "the ReleaseResources command is sent to the subarray {subarray}"
    )
)
def send_release_resources_command(
    context_fixt: SubarrayTestContextData,
    central_node_facade: TMCCentralNodeFacade,
):
    """Send the ReleaseResources command to the subarray."""
    context_fixt.when_action_name = "ReleaseResources"

    json_input = FileJSONInput("centralnode", "release_resources_mid")
    json_input = json_input.set_attribute_value("subarray_id", 1)

    context_fixt.when_action_result = central_node_facade.release_resources(
        json_input,
        wait_termination=True,
    )


@when(
    parsers.parse("the Configure command is sent to the subarray {subarray}")
)
def send_configure_command(
    context_fixt: SubarrayTestContextData,
    subarray_node_facade: TMCSubarrayNodeFacade,
):
    """Send the Configure command to the subarray."""
    context_fixt.when_action_name = "Configure"

    json_input = FileJSONInput("subarray", "configure_mid")

    # NOTE: The following line makes the test work,
    # but it is not correct since a subarray that is in IDLE state
    # state should be able to receive the Configure command.

    # time.sleep(5)

    context_fixt.when_action_result = subarray_node_facade.configure(
        json_input,
        wait_termination=True,
    )


# ------------------------------------------------------------
# Then steps


@then(
    parsers.parse(
        "the subarray {subarray} should transition to the RESOURCING state"
    )
)
def verify_resourcing_state(
    context_fixt: SubarrayTestContextData,
    subarray_node_facade: TMCSubarrayNodeFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
    event_tracer: TangoEventTracer,
):
    """Verify that the subarray transitions to the RESOURCING state."""
    assert_that(event_tracer).described_as(
        f"Both TMC Subarray Node device ({subarray_node_facade.subarray_node})"
        f", CSP Subarray device ({csp.csp_subarray}) "
        f"and SDP Subarray device ({sdp.sdp_subarray}) "
        "ObsState attribute values should move "
        f"from {str(context_fixt.starting_state)} to RESOURCING."
    ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
        subarray_node_facade.subarray_node,
        "obsState",
        ObsState.RESOURCING,
        previous_value=context_fixt.starting_state,
    ).has_change_event_occurred(
        csp.csp_subarray,
        "obsState",
        ObsState.RESOURCING,
        previous_value=context_fixt.starting_state,
    ).has_change_event_occurred(
        sdp.sdp_subarray,
        "obsState",
        ObsState.RESOURCING,
        previous_value=context_fixt.starting_state,
    )

    # for the emulated device (SDP) we verify the correct
    # Tango command has been called as expected
    verify_device_received_command(
        sdp.sdp_subarray, context_fixt.when_action_name
    )

    # override the starting state for the next step
    context_fixt.starting_state = ObsState.RESOURCING


@then(
    parsers.parse(
        "the subarray {subarray} should transition to the IDLE state"
    )
)
def verify_idle_state(
    context_fixt: SubarrayTestContextData,
    subarray_node_facade: TMCSubarrayNodeFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
    event_tracer: TangoEventTracer,
):
    """Verify that the subarray transitions to the IDLE state."""
    assert_that(event_tracer).described_as(
        f"Both TMC Subarray Node device ({subarray_node_facade.subarray_node})"
        f", CSP Subarray device ({csp.csp_subarray}) "
        f"and SDP Subarray device ({sdp.sdp_subarray}) "
        "ObsState attribute values should move "
        f"from {str(context_fixt.starting_state)} to IDLE."
    ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
        subarray_node_facade.subarray_node,
        "obsState",
        ObsState.IDLE,
        previous_value=context_fixt.starting_state,
    ).has_change_event_occurred(
        csp.csp_subarray,
        "obsState",
        ObsState.IDLE,
        previous_value=context_fixt.starting_state,
    ).has_change_event_occurred(
        sdp.sdp_subarray,
        "obsState",
        ObsState.IDLE,
        previous_value=context_fixt.starting_state,
    )


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
    """Verify that the subarray transitions to the EMPTY state."""
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


@then(
    parsers.parse(
        "the subarray {subarray} should transition to the CONFIGURING state"
    )
)
def verify_configuring_state(
    context_fixt: SubarrayTestContextData,
    subarray_node_facade: TMCSubarrayNodeFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
    event_tracer: TangoEventTracer,
):
    """Verify that the subarray transitions to the CONFIGURING state."""
    assert_that(event_tracer).described_as(
        f"Both TMC Subarray Node device ({subarray_node_facade.subarray_node})"
        f", CSP Subarray device ({csp.csp_subarray}) "
        f"and SDP Subarray device ({sdp.sdp_subarray}) "
        "ObsState attribute values should move "
        f"from {str(context_fixt.starting_state)} to CONFIGURING."
    ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
        subarray_node_facade.subarray_node,
        "obsState",
        ObsState.CONFIGURING,
        previous_value=context_fixt.starting_state,
    ).has_change_event_occurred(
        csp.csp_subarray,
        "obsState",
        ObsState.CONFIGURING,
        previous_value=context_fixt.starting_state,
    ).has_change_event_occurred(
        sdp.sdp_subarray,
        "obsState",
        ObsState.CONFIGURING,
        previous_value=context_fixt.starting_state,
    )

    # override the starting state for the next step
    context_fixt.starting_state = ObsState.CONFIGURING


@then(
    parsers.parse(
        "the subarray {subarray} should transition to the READY state"
    )
)
def verify_ready_state(
    context_fixt: SubarrayTestContextData,
    subarray_node_facade: TMCSubarrayNodeFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
    event_tracer: TangoEventTracer,
):
    """Verify that the subarray transitions to the READY state."""
    assert_that(event_tracer).described_as(
        f"Both TMC Subarray Node device ({subarray_node_facade.subarray_node})"
        f", CSP Subarray device ({csp.csp_subarray}) "
        f"and SDP Subarray device ({sdp.sdp_subarray}) "
        "ObsState attribute values should move "
        f"from {str(context_fixt.starting_state)} to READY."
    ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
        subarray_node_facade.subarray_node,
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


def _get_long_run_command_id(context_fixt: SubarrayTestContextData) -> str:
    return context_fixt.when_action_result[1][0]


def _get_expected_long_run_command_result(context_fixt) -> tuple[str, str]:
    return (_get_long_run_command_id(context_fixt), str(ResultCode.OK.value))


@then(
    parsers.parse("the central node longRunningCommand should be terminated")
)
def verify_long_running_command_result_on_central_node(
    context_fixt,
    central_node_facade: TMCCentralNodeFacade,
    event_tracer: TangoEventTracer,
):
    """Verify that the longRunningCommand is terminated."""
    assert_that(event_tracer).described_as(
        "Central Node "
        f"({central_node_facade.central_node}) "
        "longRunningCommand should be terminated."
    ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
        central_node_facade.central_node,
        "longRunningCommandResult",
        _get_expected_long_run_command_result(context_fixt),
    )


@then(
    parsers.parse(
        "the subarray {subarray} longRunningCommand should be terminated"
    )
)
def verify_long_running_command_result_on_subarray(
    context_fixt,
    subarray_node_facade: TMCSubarrayNodeFacade,
    event_tracer: TangoEventTracer,
):
    """Verify that the longRunningCommand is terminated."""
    assert_that(event_tracer).described_as(
        "TMC Subarray Node "
        f"({subarray_node_facade.subarray_node}) "
        "longRunningCommand should be terminated."
    ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
        subarray_node_facade.subarray_node,
        "longRunningCommandResult",
        _get_expected_long_run_command_result(context_fixt),
    )
