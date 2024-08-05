"""The TMC-CSP sub-arrays execute the transition from EMPTY to RESOURCING."""


import pytest
from assertpy import assert_that
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState, ResultCode
from ska_integration_test_harness.facades.csp_facade import CSPFacade
from ska_integration_test_harness.facades.sdp_facade import SDPFacade
from ska_integration_test_harness.facades.tmc_central_node_facade import (
    TMCCentralNodeFacade,
)
from ska_integration_test_harness.facades.tmc_subarray_node_facade import (
    TMCSubarrayNodeFacade,
)
from ska_integration_test_harness.inputs.obs_state_commands_input import (
    ObsStateCommandsInput,
)
from ska_tango_testing.integration import TangoEventTracer

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
    "../tmc_csp_refactor3/features/subarray_commands.feature",
    "EMPTY to RESOURCING to IDLE - CMD AssignResources",
)
def test_empty_to_resourcing_to_idle():
    """Test EMPTY to RESOURCING to IDLE transitions."""


@pytest.mark.xfail(
    reason="Without a time.sleep after the telescope reached the IDLE state, "
    "the test fails. But the test should pass without the time.sleep "
    "since if a subarray is in IDLE state, by design it should be able "
    "to receive the Configure command at any time."
)
@pytest.mark.tmc_csp_refactor3
@scenario(
    "../tmc_csp_refactor3/features/subarray_commands.feature",
    "IDLE to CONFIGURING to READY - CMD Configure",
)
def test_idle_to_configuring_to_ready():
    """Test IDLE to CONFIGURING to READY transitions."""


@pytest.mark.xfail(
    reason="Without a time.sleep after the telescope reached the IDLE state, "
    "the test fails. But the test should pass without the time.sleep "
    "since if a subarray is in IDLE state, by design it should be able "
    "to receive the Configure command at any time."
)
@pytest.mark.tmc_csp_refactor3
@scenario(
    "../tmc_csp_refactor3/features/subarray_commands.feature",
    "IDLE to RESOURCING to IDLE - CMD AssignResources",
)
def test_idle_to_resourcing_to_idle():
    """Test IDLE to RESOURCING to IDLE transitions."""


@pytest.mark.xfail(
    reason="Without a time.sleep after the telescope reached the IDLE state, "
    "the test fails. But the test should pass without the time.sleep "
    "since if a subarray is in IDLE state, by design it should be able "
    "to receive the Configure command."
)
@pytest.mark.tmc_csp_refactor3
@scenario(
    "../tmc_csp_refactor3/features/subarray_commands.feature",
    "IDLE to RESOURCING to EMPTY - CMD ReleaseResources",
)
def test_idle_to_resourcing_to_empty():
    """Test IDLE to RESOURCING to EMPTY transitions."""


@pytest.mark.tmc_csp_refactor3
@scenario(
    "../tmc_csp_refactor3/features/subarray_commands.feature",
    "READY to SCANNING to READY- CMD Scan",
)
def test_ready_to_scanning_to_ready():
    """Test READY to SCANNING to READY transitions."""


@pytest.mark.tmc_csp_refactor3
@scenario(
    "../tmc_csp_refactor3/features/subarray_commands.feature",
    "READY to IDLE - CMD End",
)
def test_ready_to_idle():
    """Test READY to IDLE transitions."""


@pytest.mark.xfail(
    reason="Without a time.sleep after the telescope reached the READY state, "
    "the test fails. But the test should pass without the time.sleep "
    "since if a subarray is in READY state, by design it should be able "
    "to receive the Configure command."
)
@pytest.mark.tmc_csp_refactor3
@scenario(
    "../tmc_csp_refactor3/features/subarray_commands.feature",
    "READY to CONFIGURING to READY - CMD Configure",
)
def test_ready_to_configuring_to_ready():
    """Test READY to CONFIGURING to READY transitions."""


@pytest.mark.tmc_csp_refactor3
@scenario(
    "../tmc_csp_refactor3/features/subarray_commands.feature",
    "SCANNING to READY - CMD End Scan",
)
def test_scanning_to_ready():
    """Test SCANNING to READY transitions."""
    pass


# ------------------------------------------------------------
# Given steps


# The initial common Given steps are already defined in conftest.py


@given(parsers.parse("the subarray {subarray} is in the EMPTY state"))
def subarray_in_empty_state(
    context_fixt: SubarrayTestContextData,
    subarray_node_facade: TMCSubarrayNodeFacade,
):
    """
    Set the specified subarray to the EMPTY state.

    This step uses the TMCSubarrayNodeFacade to force the subarray's
    ObsState to EMPTY. It does this by calling the force_change_of_obs_state
    method, which bypasses normal state transition checks. The method is
    invoked with ObsState.EMPTY and an empty ObsStateCommandsInput,
    ensuring a direct transition regardless of the current state.
    The operation waits for completion.

    The step also updates the starting_state in the test context data
    to reflect this EMPTY state, which can be useful for test assertions
    or subsequent test steps.
    """
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
        "the AssignResources command is sent to the subarray {subarray} "
        "and the Assigned event is induced"
    )
)
def send_assign_resources_command(
    context_fixt: SubarrayTestContextData,
    central_node_facade: TMCCentralNodeFacade,
):
    """Send the AssignResources command to the subarray.

    This step uses the central_node_facade to send an AssignResources command
    to the specified subarray. It uses a pre-defined JSON input file,
    modifies the subarray_id, and sends the command without waiting for
    termination. The action result is stored in the context fixture."""
    context_fixt.when_action_name = "AssignResources"

    json_input = FileJSONInput("centralnode", "assign_resources_mid")
    json_input = json_input.set_attribute_value("subarray_id", 1)

    context_fixt.when_action_result = central_node_facade.assign_resources(
        json_input,
        wait_termination=False,
    )


@when(
    parsers.parse(
        "the AssignResources command is sent to the subarray {subarray} "
        "to assign additional resources"
    )
)
def send_assign_additional_resources_command(
    context_fixt: SubarrayTestContextData,
    central_node_facade: TMCCentralNodeFacade,
):
    """
    Send the AssignResources command to assign additional resources.

    This step is similar to the basic AssignResources command, but it's
    intended to assign additional resources to the subarray. Currently,
    it uses the same input as the basic command, but this is noted as
    needing to be changed in the future.
    """
    context_fixt.when_action_name = "AssignResources"

    # TODO: change this input to assign additional resources
    json_input = FileJSONInput("centralnode", "assign_resources_mid")
    json_input = json_input.set_attribute_value("subarray_id", 1)

    context_fixt.when_action_result = central_node_facade.assign_resources(
        json_input,
        wait_termination=False,
    )


@when(
    parsers.parse(
        "the ReleaseResources command is sent to the subarray {subarray} "
        "and the All released event is induced"
    )
)
def send_release_resources_command(
    context_fixt: SubarrayTestContextData,
    central_node_facade: TMCCentralNodeFacade,
):
    """
    Send the ReleaseResources command to the subarray.

    This step uses the central_node_facade to send a ReleaseResources
    command to the specified subarray. It uses a pre-defined JSON input
    file, modifies the subarray_id, and sends the command without waiting
    for termination. The action result is stored in the context fixture.
    """
    context_fixt.when_action_name = "ReleaseResources"

    json_input = FileJSONInput("centralnode", "release_resources_mid")
    json_input = json_input.set_attribute_value("subarray_id", 1)

    context_fixt.when_action_result = central_node_facade.release_resources(
        json_input,
        wait_termination=False,
    )


@when(
    parsers.parse("the Configure command is sent to the subarray {subarray}")
)
def send_configure_command(
    context_fixt: SubarrayTestContextData,
    subarray_node_facade: TMCSubarrayNodeFacade,
):
    """
    Send the Configure command to the subarray.

    This step uses the subarray_node_facade to send a Configure command
    to the specified subarray. It uses a pre-defined JSON input file and
    sends the command without waiting for termination. The action result
    is stored in the context fixture.
    """
    context_fixt.when_action_name = "Configure"

    json_input = FileJSONInput("subarray", "configure_mid")

    context_fixt.when_action_result = subarray_node_facade.configure(
        json_input,
        wait_termination=False,
    )


@when(parsers.parse("the Scan command is sent to the subarray {subarray}"))
def send_scan_command(
    context_fixt: SubarrayTestContextData,
    subarray_node_facade: TMCSubarrayNodeFacade,
):
    """
    Send the Scan command to the subarray.

    This step uses the subarray_node_facade to send a Scan command to the
    specified subarray. It uses a pre-defined JSON input file and sends
    the command without waiting for termination. The action result is
    stored in the context fixture.
    """
    context_fixt.when_action_name = "Scan"

    json_input = FileJSONInput("subarray", "scan_mid")

    context_fixt.when_action_result = subarray_node_facade.scan(
        json_input,
        wait_termination=False,
    )


@when(parsers.parse("the End command is sent to the subarray {subarray}"))
def send_end_command(
    context_fixt: SubarrayTestContextData,
    subarray_node_facade: TMCSubarrayNodeFacade,
):
    """
    Send the End command to the subarray.

    This step uses the subarray_node_facade to send an End command to the
    specified subarray. It sends the command without waiting for termination
    and stores the action result in the context fixture.
    """
    context_fixt.when_action_name = "End"

    context_fixt.when_action_result = subarray_node_facade.end_observation(
        wait_termination=False,
    )


@when(parsers.parse("the EndScan command is sent to the subarray {subarray}"))
def send_end_scan_command(
    context_fixt: SubarrayTestContextData,
    subarray_node_facade: TMCSubarrayNodeFacade,
):
    """
    Send the EndScan command to the subarray.

    This step uses the subarray_node_facade to send an EndScan command to
    the specified subarray. It sends the command without waiting for
    termination and stores the action result in the context fixture.
    """
    context_fixt.when_action_name = "EndScan"

    context_fixt.when_action_result = subarray_node_facade.end_scan(
        wait_termination=False,
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
    """
    Verify the subarray's transition to the RESOURCING state.

    This step checks that the ObsState attribute of the TMC Subarray Node,
    CSP Subarray, and SDP Subarray devices all transition from the starting
    state to the RESOURCING state. It uses the event_tracer to assert that
    these state changes occur within a specified timeout. For the SDP device,
    it also verifies that the correct Tango command was received. Finally,
    it updates the starting state in the context fixture for subsequent steps.
    """
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
    """
    Verify the subarray's transition to the IDLE state.

    This step checks that the ObsState attribute of the TMC Subarray Node,
    CSP Subarray, and SDP Subarray devices all transition from the starting
    state to the IDLE state. It uses the event_tracer to assert that these
    state changes occur within a specified timeout.
    """
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
    """
    Verify the subarray's transition to the EMPTY state.

    This step checks that the ObsState attribute of the TMC Subarray Node,
    CSP Subarray, and SDP Subarray devices all transition from the starting
    state to the EMPTY state. It uses the event_tracer to assert that these
    state changes occur within a specified timeout.
    """
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
    """
    Verify the subarray's transition to the CONFIGURING state.

    This step checks that the ObsState attribute of the TMC Subarray Node,
    CSP Subarray, and SDP Subarray devices all transition from the starting
    state to the CONFIGURING state. It uses the event_tracer to assert that
    these state changes occur within a specified timeout. After verification,
    it updates the starting state in the context fixture for subsequent steps.
    """
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
    """
    Verify the subarray's transition to the READY state.

    This step checks that the ObsState attribute of the TMC Subarray Node,
    CSP Subarray, and SDP Subarray devices all transition from the starting
    state to the READY state. It uses the event_tracer to assert that these
    state changes occur within a specified timeout. After verification, it
    updates the starting state in the context fixture for subsequent steps.
    """
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


@then(
    parsers.parse(
        "the subarray {subarray} should transition to the SCANNING state"
    )
)
def verify_scanning_state(
    context_fixt: SubarrayTestContextData,
    subarray_node_facade: TMCSubarrayNodeFacade,
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
        f"Both TMC Subarray Node device ({subarray_node_facade.subarray_node})"
        f", CSP Subarray device ({csp.csp_subarray}) "
        f"and SDP Subarray device ({sdp.sdp_subarray}) "
        "ObsState attribute values should move "
        f"from {str(context_fixt.starting_state)} to SCANNING."
    ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
        subarray_node_facade.subarray_node,
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


def _get_long_run_command_id(context_fixt: SubarrayTestContextData) -> str:
    return context_fixt.when_action_result[1][0]


def _get_expected_long_run_command_result(context_fixt) -> tuple[str, str]:
    return (_get_long_run_command_id(context_fixt), str(ResultCode.OK.value))


@then(
    parsers.parse(
        "the central node reports a longRunningCommand successful completion"
    )
)
def verify_long_running_command_result_on_central_node(
    context_fixt,
    central_node_facade: TMCCentralNodeFacade,
    event_tracer: TangoEventTracer,
):
    """
    Verify the successful completion of a longRunningCommand on central node.

    This step checks that the TMC Central Node reports a successful completion
    of a longRunningCommand. It uses the event_tracer to assert that a change
    event occurred on the longRunningCommandResult attribute within a specified
    timeout. The expected result is derived from the context fixture.
    """
    assert_that(event_tracer).described_as(
        "TMC Central Node "
        f"({central_node_facade.central_node}) "
        "is expected to report a"
        "longRunningCommand successful completion."
    ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
        central_node_facade.central_node,
        "longRunningCommandResult",
        _get_expected_long_run_command_result(context_fixt),
    )


@then(
    parsers.parse(
        "the subarray {subarray} reports "
        "a longRunningCommand successful completion"
    )
)
def verify_long_running_command_result_on_subarray(
    context_fixt,
    subarray_node_facade: TMCSubarrayNodeFacade,
    event_tracer: TangoEventTracer,
):
    """
    Verify the successful completion of a longRunningCommand on the subarray.

    This step checks that the TMC Subarray Node reports a successful completion
    of a longRunningCommand. It uses the event_tracer to assert that a change
    event occurred on the longRunningCommandResult attribute within a specified
    timeout. The expected result is derived from the context fixture.
    """
    assert_that(event_tracer).described_as(
        "TMC Subarray Node "
        f"({subarray_node_facade.subarray_node}) "
        "is expected to report a"
        "longRunningCommand successful completion."
    ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
        subarray_node_facade.subarray_node,
        "longRunningCommandResult",
        _get_expected_long_run_command_result(context_fixt),
    )
