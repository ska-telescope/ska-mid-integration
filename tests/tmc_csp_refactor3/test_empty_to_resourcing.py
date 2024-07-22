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


@pytest.mark.tmc_csp_refactor3
@scenario(
    "../features/obsstate_valid_single_transitions.feature",
    "EMPTY to RESOURCING - CMD AssignResources (6)",
)
def test_empty_to_resourcing():
    """Test EMPTY to RESOURCING transition."""


# The initial common Given steps are already defined in conftest.py


@given(parsers.parse("the subarray 001 is in the EMPTY state"))
def subarray_in_empty_state(
    context_fixt,
    subarray_node_facade: TMCSubarrayNodeFacade,
):
    """Ensure the subarray is in the EMPTY state."""
    context_fixt["starting_state"] = ObsState.EMPTY
    subarray_node_facade.force_change_of_obs_state(
        ObsState.EMPTY,
        ObsStateCommandsInput(),
        wait_termination=True,
    )


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


@then(
    parsers.parse("the subarray 001 should transition to the RESOURCING state")
)
def verify_resourcing_state(
    context_fixt,
    subarray_node_facade: TMCSubarrayNodeFacade,
    csp: CSPFacade,
    event_tracer: TangoEventTracer,
):
    """Verify that the subarray transitions to the RESOURCING state."""
    assert_that(event_tracer).described_as(
        f"Both TMC Subarray Node device ({subarray_node_facade.subarray_node})"
        f" and CSP Subarray device ({csp.csp_subarray}) "
        "ObsState attribute values should move to RESOURCING."
    ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
        subarray_node_facade.subarray_node,
        "obsState",
        ObsState.RESOURCING,
        previous_value=context_fixt["starting_state"],
    ).has_change_event_occurred(
        csp.csp_subarray,
        "obsState",
        ObsState.RESOURCING,
        previous_value=context_fixt["starting_state"],
    )
