"""The TMC-CSP sub-arrays execute the transition from EMPTY to RESOURCING."""


import pytest
from assertpy import assert_that
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState
from ska_tango_testing.integration import TangoEventTracer

from tests.test_harness3.telescope_facades.csp_facade import CSPFacade
from tests.test_harness3.telescope_facades.tmc_subarray_node_facade import (
    TMCSubarrayNodeFacade,
)
from tests.test_harness3.telescope_inputs.obs_state_commands_input import (
    ObsStateCommandsInput,
)
from tests.various_utils.file_json_input import FileJSONInput

ASSERTIONS_TIMEOUT = 60

# ----------------------------------------------------------
# IDLE -> X transitions scenarios


@pytest.mark.skip("Not needed for now")
@pytest.mark.tmc_csp_refactor3
@scenario(
    "../features/obsstate_valid_single_transitions.feature",
    "IDLE to CONFIGURING - CMD Configure (16)",
)
def test_idle_to_configuring():
    """Test IDLE to CONFIGURING transition."""


@pytest.mark.skip("Not needed for now")
@pytest.mark.tmc_csp_refactor3
@scenario(
    "../features/obsstate_valid_single_transitions.feature",
    "IDLE to RESOURCING - CMD ReleaseResources (17)",
)
def test_idle_to_resourcing_through_release():
    """Test IDLE to RESOURCING transition (through ReleaseResources)."""


@pytest.mark.skip("Not needed for now")
@pytest.mark.tmc_csp_refactor3
@scenario(
    "../features/obsstate_valid_single_transitions.feature",
    "IDLE to RESOURCING - CMD AssignResources (18)",
)
def test_idle_to_resourcing_through_assign():
    """Test IDLE to RESOURCING transition (through AssignResources)."""


@pytest.mark.skip("Not needed for now")
@pytest.mark.tmc_csp_refactor3
@scenario(
    "../features/obsstate_valid_single_transitions.feature",
    "IDLE to ABORTING - CMD Abort (19)",
)
def test_idle_to_aborting():
    """Test IDLE to ABORTING transition."""


# ----------------------------------------------------------
# Steps implementations


@given(parsers.parse("the subarray 001 is in the IDLE state"))
def subarray_in_idle_state(
    context_fixt,
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


@when(parsers.parse("the Configure command is sent to the subarray 001"))
def send_configure_command(
    context_fixt,
    subarray_node_facade: TMCSubarrayNodeFacade,
):
    """Send the Configure command to the subarray."""
    context_fixt["trigger"] = "Configure"
    subarray_node_facade.configure(
        FileJSONInput("subarray", "configure_mid"), wait_termination=False
    )


@when(
    parsers.parse("the ReleaseResources command is sent to the subarray 001")
)
def send_release_resources_command(
    context_fixt,
    subarray_node_facade: TMCSubarrayNodeFacade,
):
    """Send the ReleaseResources command to the subarray."""
    context_fixt["trigger"] = "ReleaseResources"
    subarray_node_facade.release_all_resources(wait_termination=False)


@when(parsers.parse("the AssignResources command is sent to the subarray 001"))
def send_assign_resources_command(
    context_fixt,
    subarray_node_facade: TMCSubarrayNodeFacade,
):
    """Send the AssignResources command to the subarray."""
    context_fixt["trigger"] = "AssignResources"
    subarray_node_facade.assign_resources(
        FileJSONInput("subarray", "assign_resources_mid"),
        wait_termination=False,
    )


@when(parsers.parse("the Abort command is sent to the subarray 001"))
def send_abort_command(
    context_fixt,
    subarray_node_facade: TMCSubarrayNodeFacade,
    event_tracer: TangoEventTracer,
):
    """Send the Abort command to the subarray."""
    context_fixt["trigger"] = "Abort"
    subarray_node_facade.abort(wait_termination=False)

    # if starting_state in TRANSIENT_STATES:
    # assert_that(event_tracer).described_as(
    #     "FAILED ASSUMPTION: "
    #     "TMC Subarray Node device "
    #     f"({subarray_node_facade.subarray_node}) "
    #     "Abort command invocation has been performed "
    #     f"after obsState is {starting_state}, "
    #     "because automatic transaction triggered."
    # ).hasnt_change_event_occurred(
    #     subarray_node_facade.subarray_node,
    #     "obsState",
    #     ObsState.ABORTING,
    #     previous_value=starting_state,
    # )


@then(
    parsers.parse(
        "the subarray 001 should transition to the CONFIGURING state"
    )
)
def verify_configuring_state(
    context_fixt,
    subarray_node_facade: TMCSubarrayNodeFacade,
    csp: CSPFacade,
    event_tracer: TangoEventTracer,
):
    """Verify that the subarray transitions to the CONFIGURING state."""
    assert_that(event_tracer).described_as(
        f"Both TMC Subarray Node device ({subarray_node_facade.subarray_node})"
        f" and CSP Subarray device ({csp.csp_subarray}) "
        "ObsState attribute values should move to CONFIGURING"
        "from READY."
    ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
        subarray_node_facade.subarray_node,
        "obsState",
        ObsState.CONFIGURING,
        previous_value=context_fixt["starting_state"],
    ).has_change_event_occurred(
        csp.csp_subarray,
        "obsState",
        ObsState.CONFIGURING,
        previous_value=context_fixt["starting_state"],
    )


# @then(
#     parsers.parse("the subarray 001 should transition to the ABORTING state")
# )
# def verify_aborting_state(
#     context_fixt,
#     subarray_node_facade: TMCSubarrayNodeFacade,
#     csp: CSPFacade,
#     event_tracer: TangoEventTracer,
# ):
#     """Verify that the subarray transitions to the ABORTING state."""
#     assert_that(event_tracer).described_as(
#         f"Both TMC Subarray Node device ({subarray_node_facade.subarray_node})" # pylint: disable=line-too-long # noqa E501
#         f" and CSP Subarray device ({csp.csp_subarray}) "
#         "ObsState attribute values should move to ABORTING."
#     ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
#         subarray_node_facade.subarray_node,
#         "obsState",
#         ObsState.ABORTING,
#         previous_value=context_fixt["starting_state"],
#     ).has_change_event_occurred(
#         csp.csp_subarray,
#         "obsState",
#         ObsState.ABORTING,
#         previous_value=context_fixt["starting_state"],
#     )

#     assert_that(event_tracer).described_as(
#         f"Both TMC Subarray Node device ({subarray_node_facade.subarray_node})" # pylint: disable=line-too-long # noqa E501
#         f" and CSP Subarray device ({csp.csp_subarray}) "
#         "ObsState attribute values should move to ABORTED."
#     ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
#         subarray_node_facade.subarray_node,
#         "obsState",
#         ObsState.ABORTED,
#         previous_value=context_fixt["starting_state"],
#     ).has_change_event_occurred(
#         csp.csp_subarray,
#         "obsState",
#         ObsState.ABORTED,
#         previous_value=context_fixt["starting_state"],
#     )
