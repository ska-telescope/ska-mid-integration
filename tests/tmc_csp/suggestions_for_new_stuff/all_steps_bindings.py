"""Test module for TMC-CSP Obsstate transitions functionality."""
import pytest
from pytest_bdd import given, when, scenario, parsers, then
from ska_control_model import ObsState
from ska_tango_testing.integration import TangoEventTracer

from tests.test_harness3.helpers import (
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
)
from tests.test_harness3.telescope_facades.csp_facade import CSPFacade
from tests.test_harness3.telescope_facades.tmc_central_node_facade import (
    TMCCentralNodeFacade,
)
from tests.test_harness3.telescope_facades.tmc_subarray_node_facade import (
    TMCSubarrayNodeFacade,
)
from tests.test_harness3.utils.common_utils import JsonFactory


from assertpy import assert_that

ASSERTIONS_TIMEOUT = 60

@pytest.mark.tmc_csp
@scenario("../features/subarray_001_state_transitions.feature", "EMPTY to RESOURCING - CMD AssignResources (6)")
def test_empty_to_resourcing():
    """Test EMPTY to RESOURCING transition."""

# TODO add test definitions for all other scenarios


# Define a fixture to store things, like the starting state
@pytest.fixture
def context_fixt():
    return {'starting_state':None,
            'trigger':None,}

TRANSIENT_STATES=[ObsState.ABORTING, ObsState.RESTARTING,
                  ObsState.RESOURCING, ObsState.CONFIGURING,
                  ObsState.SCANNING, ObsState.RESETTING,]

def _setup_event_subscriptions(
    subarray_node_facade: TMCSubarrayNodeFacade,
    csp: CSPFacade,
    event_tracer: TangoEventTracer,
):
    """Set up event subscriptions for the test.

    Args:
        subarray_node_facade: Facade for the TMC subarray node.
        csp: Facade for the CSP.
        event_tracer: Event tracer for capturing events.
    """
    event_tracer.subscribe_event(csp.csp_subarray, "obsState")
    event_tracer.subscribe_event(
        subarray_node_facade.subarray_node, "obsState"
    )
    log_events(
        {
            csp.csp_subarray: ["obsState"],
            subarray_node_facade.subarray_node: ["obsState"],
        }
    )

# DECIDED to let the automatic teardown handle this
# def _wait_for_quiescence_of_subarray(csp, event_tracer, subarray_node_facade):
#     """ Wait for the subarray to reach the EMPTY state.
#     It assumes that the command RESTART has been sent to the subarray."""
#     # Clean up
#     assert_that(event_tracer).described_as(
#         f"ASSUMPTION. \n"
#         f"TMC Subarray Node device ({subarray_node_facade.subarray_node})"
#         f"ObsState attribute value is expected to be EMPTY."
#     ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
#         subarray_node_facade.subarray_node,
#         "obsState",
#         ObsState.EMPTY,
#     ).has_change_event_occurred(
#         csp.csp_subarray,
#         "obsState",
#         ObsState.EMPTY
#     )

@given("the telescope is ON state")
def given_telescope_turned_on(
    subarray_node_facade: TMCSubarrayNodeFacade,
    central_node_facade: TMCCentralNodeFacade,
    csp: CSPFacade,
    event_tracer: TangoEventTracer,
):
    """Ensure the telescope is in ON state."""
    central_node_facade.move_to_on(wait_termination=True)

@given("the subarray {subarray_id} can be used")
def subarray_can_be_used(
        subarray_node_facade: TMCSubarrayNodeFacade,
        csp: CSPFacade,
        event_tracer: TangoEventTracer,
        subarray_id: str,
    ):
    subarray_node_facade.set_subarray_id(subarray_id)
    _setup_event_subscriptions(subarray_node_facade, csp, event_tracer)
    

@given(parsers.parse("the subarray {subarray_id} is in the EMPTY state"))
def subarray_in_empty_state(context_fixt,
    subarray_id: str,
    subarray_node_facade: TMCSubarrayNodeFacade,
):
    """Ensure the subarray is in the EMPTY state."""
    context_fixt["starting_state"]=ObsState.EMPTY
    subarray_node_facade.force_change_of_obs_state(
        ObsState.EMPTY,
        wait_termination_condition=True,
    )

@given(parsers.parse("the subarray {subarray_id} is in the RESOURCING state"))
def subarray_in_resourcing_state(context_fixt,
    subarray_id: str,
    subarray_node_facade: TMCSubarrayNodeFacade,
    command_input_factory: JsonFactory,
):
    """Ensure the subarray is in the RESOURCING state."""

    context_fixt["starting_state"]=ObsState.RESOURCING
    subarray_node_facade.force_change_of_obs_state(
        ObsState.RESOURCING,
        assign_input_json=prepare_json_args_for_centralnode_commands(
            "assign_resources_mid", command_input_factory
        ),
        wait_termination_condition=True,
    )

@given(parsers.parse("the subarray {subarray_id} is in the IDLE state"))
def subarray_in_idle_state(context_fixt,
    subarray_id: str,
    subarray_node_facade: TMCSubarrayNodeFacade,
    command_input_factory: JsonFactory,
):
    """Ensure the subarray is in the IDLE state."""

    context_fixt["starting_state"]=ObsState.IDLE
    subarray_node_facade.force_change_of_obs_state(
        ObsState.IDLE,
        assign_input_json=prepare_json_args_for_centralnode_commands(
            "assign_resources_mid", command_input_factory
        ),
        wait_termination_condition=True,
    )

@given(parsers.parse("the subarray {subarray_id} is in the CONFIGURING state"))
def subarray_in_configuring_state(context_fixt,
    subarray_id: str,
    subarray_node_facade: TMCSubarrayNodeFacade,
    command_input_factory: JsonFactory,
):
    context_fixt["starting_state"]=ObsState.CONFIGURING
    """Ensure the subarray is in the CONFIGURING state."""
    subarray_node_facade.force_change_of_obs_state(
        ObsState.CONFIGURING,
        assign_input_json=prepare_json_args_for_centralnode_commands(
            "assign_resources_mid", command_input_factory
        ),
        configure_input_json=prepare_json_args_for_commands(
            "configure_mid", command_input_factory
        ),
        wait_termination_condition=True,
    )

@given(parsers.parse("the subarray {subarray_id} is in the READY state"))
def subarray_in_ready_state(context_fixt,
    subarray_id: str,
    subarray_node_facade: TMCSubarrayNodeFacade,
    command_input_factory: JsonFactory,
):
    """Ensure the subarray is in the READY state."""
    context_fixt["starting_state"]=ObsState.READY
    subarray_node_facade.force_change_of_obs_state(
        ObsState.READY,
        assign_input_json=prepare_json_args_for_centralnode_commands(
            "assign_resources_mid", command_input_factory
        ),
        configure_input_json=prepare_json_args_for_commands(
            "configure_mid", command_input_factory
        ),
        wait_termination_condition=True,
    )

@given(parsers.parse("the subarray {subarray_id} is in the SCANNING state"))
def subarray_in_scanning_state(context_fixt,
    subarray_id: str,
    subarray_node_facade: TMCSubarrayNodeFacade,
    command_input_factory: JsonFactory,
):
    """Ensure the subarray is in the SCANNING state."""

    context_fixt["starting_state"]=ObsState.SCANNING
    subarray_node_facade.force_change_of_obs_state(
        ObsState.SCANNING,
        assign_input_json=prepare_json_args_for_centralnode_commands(
            "assign_resources_mid", command_input_factory
        ),
        configure_input_json=prepare_json_args_for_commands(
            "configure_mid", command_input_factory
        ),
        scan_input_json=prepare_json_args_for_commands(
            "scan_mid", command_input_factory
        ),
        wait_termination_condition=True,
    )

@given(parsers.parse("the subarray {subarray_id} is in the ABORTED state"))
def subarray_in_aborted_state(context_fixt,
    subarray_id: str,
    subarray_node_facade: TMCSubarrayNodeFacade,
):
    """Ensure the subarray is in the ABORTED state."""

    context_fixt["starting_state"]=ObsState.ABORTED
    subarray_node_facade.force_change_of_obs_state(
        ObsState.ABORTED,
        wait_termination_condition=True,
    )

@given(parsers.parse("the subarray {subarray_id} is in the OBS_FAULT state"))
def subarray_in_obs_fault_state(context_fixt,
    subarray_id: str,
    subarray_node_facade: TMCSubarrayNodeFacade,
):
    """Ensure the subarray is in the OBS_FAULT state."""

    context_fixt["starting_state"]=ObsState.OBS_FAULT
    subarray_node_facade.force_change_of_obs_state(
        ObsState.OBS_FAULT,
        wait_termination_condition=True,
    )





@given(parsers.parse("the subarray {subarray_id} is in the ABORTING state"))
def subarray_in_obs_fault_state(context_fixt,
                                subarray_id: str,
                                subarray_node_facade: TMCSubarrayNodeFacade,
                                ):

    context_fixt["starting_state"] = ObsState.ABORTING
    subarray_node_facade.force_change_of_obs_state(
        ObsState.ABORTING,
        wait_termination_condition=True,
    )



@given(parsers.parse("the subarray {subarray_id} is in the RESTARTING state"))
def subarray_in_obs_fault_state(context_fixt,
    subarray_id: str,
    subarray_node_facade: TMCSubarrayNodeFacade,
):

    context_fixt["starting_state"]=ObsState.RESTARTING
    subarray_node_facade.force_change_of_obs_state(
        ObsState.RESTARTING,
        wait_termination_condition=True,
    )










@when(parsers.parse("the AssignResources command is sent to the subarray {subarray_id}"))
def send_assign_resources_command(context_fixt,
    subarray_id: str,
    subarray_node_facade: TMCSubarrayNodeFacade,
    command_input_factory: JsonFactory,
):
    """Send the AssignResources command to the subarray."""
    context_fixt["trigger"]="AssignResources"
    command_input_json = prepare_json_args_for_commands(
        "assign_resources_mid", command_input_factory
    )
    subarray_node_facade.assign_resources(command_input_json, wait_termination_condition=False)

@when(parsers.parse("the Abort command is sent to the subarray {subarray_id}"))
def send_abort_command(context_fixt,
    subarray_id: str,
    subarray_node_facade: TMCSubarrayNodeFacade,
    event_tracer: TangoEventTracer,
):
    context_fixt["trigger"]="Abort"
    """Send the Abort command to the subarray."""
    
    starting_state=context_fixt["starting_state"]
    subarray_node_facade.abort(wait_termination_condition=False)
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

@when(parsers.parse("the Configure command is sent to the subarray {subarray_id}"))
def send_configure_command(context_fixt,
    subarray_id: str,
    subarray_node_facade: TMCSubarrayNodeFacade,
    command_input_factory: JsonFactory,
):
    """Send the Configure command to the subarray."""

    context_fixt["trigger"]="Configure"
    command_input_json = prepare_json_args_for_commands(
        "configure_mid", command_input_factory
    )
    subarray_node_facade.configure(command_input_json, wait_termination_condition=False)

@when(parsers.parse("the ReleaseResources command is sent to the subarray {subarray_id}"))
def send_release_resources_command(context_fixt,
    subarray_id: str,
    subarray_node_facade: TMCSubarrayNodeFacade,
):
    """Send the ReleaseResources command to the subarray."""

    context_fixt["trigger"]="ReleaseResources"
    subarray_node_facade.release_resources(wait_termination_condition=False)

@when(parsers.parse("the Scan command is sent to the subarray {subarray_id}"))
def send_scan_command(context_fixt,
    subarray_id: str,
    subarray_node_facade: TMCSubarrayNodeFacade,
    command_input_factory: JsonFactory,
):
    """Send the Scan command to the subarray."""

    context_fixt["trigger"]="Scan"
    command_input_json = prepare_json_args_for_commands(
        "scan_mid", command_input_factory
    )
    subarray_node_facade.scan(command_input_json, wait_termination_condition=False)

@when(parsers.parse("the End command is sent to the subarray {subarray_id}"))
def send_end_command(context_fixt,
    subarray_id: str,
    subarray_node_facade: TMCSubarrayNodeFacade,
):
    """Send the End command to the subarray."""

    context_fixt["trigger"]="End"
    subarray_node_facade.end(wait_termination_condition=False)

@when(parsers.parse("the EndScan command is sent to the subarray {subarray_id}"))
def send_end_scan_command(context_fixt,
    subarray_id: str,
    subarray_node_facade: TMCSubarrayNodeFacade,
):
    """Send the EndScan command to the subarray."""

    context_fixt["trigger"]="EndScan"
    subarray_node_facade.end_scan(wait_termination_condition=False)

@when(parsers.parse("the Restart command is sent to the subarray {subarray_id}"))
def send_restart_command(context_fixt,
    subarray_id: str,
    subarray_node_facade: TMCSubarrayNodeFacade,
):
    """Send the Restart command to the subarray."""
    context_fixt["trigger"]="Restart"
    
    subarray_node_facade.restart(wait_termination_condition=False)


@when(parsers.parse("the subarray {subarray_id} is in the EMPTY state and an observation fault occurs"))
def subarray_in_empty_state_and_obs_fault(context_fixt,
    subarray_id: str,
    subarray_node_facade: TMCSubarrayNodeFacade,):

    context_fixt["starting_state"]=ObsState.EMPTY
    # TODO find out how to do this
    induce_obs_fault(subarray_node_facade)
    subarray_node_facade.force_change_of_obs_state(
        ObsState.EMPTY,
        wait_termination_condition=True,
    )


@when(parsers.parse("the subarray {subarray_id} is in the RESOURCING state and the Assigned event is induced"))
def subarray_in_resourcing_state_and_assigned_event(context_fixt,
    subarray_id: str,
    subarray_node_facade: TMCSubarrayNodeFacade,
    csp: CSPFacade,
    event_tracer: TangoEventTracer,
):
    starting_state = ObsState.RESOURCING
    context_fixt["starting_state"]=starting_state
    subarray_node_facade.force_change_of_obs_state(
        starting_state,
        assign_input_json=prepare_json_args_for_centralnode_commands(
            "assign_resources_mid", command_input_factory
        ),
        wait_termination_condition=True,
    )
    # no specific action is needed to induce the assigned event

@when(parsers.parse("the subarray {subarray_id} is in the RESOURCING state and the Released event is induced"))
def subarray_in_resourcing_state_and_released_event(context_fixt,
    subarray_id: str,
    subarray_node_facade: TMCSubarrayNodeFacade,
    csp: CSPFacade,
    event_tracer: TangoEventTracer,
):
    starting_state = ObsState.RESOURCING
    context_fixt["starting_state"]=starting_state
    # here we change the input json to induce the released event
    subarray_node_facade.force_change_of_obs_state(
        starting_state,
        assign_input_json=prepare_json_args_for_centralnode_commands(
            "assign_resources_mid_for_released", command_input_factory
        ),
        wait_termination_condition=True,
    )


@when(parsers.parse("the subarray {subarray_id} is in the RESOURCING state and the All released event is induced"))
def subarray_in_resourcing_state_and_all_released_event(context_fixt,
    subarray_id: str,
    subarray_node_facade: TMCSubarrayNodeFacade,
    csp: CSPFacade,
    event_tracer: TangoEventTracer,
):
    starting_state = ObsState.RESOURCING
    context_fixt["starting_state"]=starting_state
    # here we change the input json to induce the all released event
    subarray_node_facade.force_change_of_obs_state(
        starting_state,
        assign_input_json=prepare_json_args_for_centralnode_commands(
            "assign_resources_mid_for_all_released", command_input_factory
        ),
        wait_termination_condition=True,
    )

@when(parsers.parse("the subarray {subarray_id} is in the RESOURCING state and an observation fault occurs"))
def subarray_in_resourcing_state_and_obs_fault(context_fixt,
    subarray_id: str,
    subarray_node_facade: TMCSubarrayNodeFacade,):

    context_fixt["starting_state"]=ObsState.RESOURCING
    # TODO find out how to do this
    induce_obs_fault(subarray_node_facade)
    subarray_node_facade.force_change_of_obs_state(
        ObsState.RESOURCING,
        wait_termination_condition=True,
    )

@when(parsers.parse("the subarray {subarray_id} is in the IDLE state and an observation fault occurs"))
def subarray_in_idle_state_and_obs_fault(context_fixt,
    subarray_id: str,
    subarray_node_facade: TMCSubarrayNodeFacade,):

    context_fixt["starting_state"]=ObsState.IDLE
    # TODO find out how to do this
    induce_obs_fault(subarray_node_facade)
    subarray_node_facade.force_change_of_obs_state(
        ObsState.IDLE,
        wait_termination_condition=True,
    )

# TODO implement the remaining WHEN steps

@then(parsers.parse("the subarray {subarray_id} should transition to the EMPTY state"))
def verify_empty_state(context_fixt,
    subarray_id: str,
    subarray_node_facade: TMCSubarrayNodeFacade,
    csp: CSPFacade,
    event_tracer: TangoEventTracer,
):
    """Verify that the subarray transitions to the EMPTY state."""
    (assert_that(event_tracer).described_as(
        f"Both TMC Subarray Node device ({subarray_node_facade.subarray_node})"
        f" and CSP Subarray device ({csp.csp_subarray}) "
        "ObsState attribute values should move to EMPTY."
    ).within_timeout(ASSERTIONS_TIMEOUT)
    .have_events_occurred( # let's check for a tuple of events, all of them within the same timeout
        # TODO this is a new custom assertion that needs to be implemented
        (subarray_node_facade.subarray_node,
        "obsState",
        ObsState.EMPTY,
        previous_value=context_fixt["starting_state"]),
        (csp.csp_subarray,
        "obsState",
        ObsState.EMPTY,
        previous_value=context_fixt["starting_state"])
    ))



@then(parsers.parse("the subarray {subarray_id} should transition to the RESOURCING state"))
def verify_resourcing_state(context_fixt,
    subarray_id: str,
    subarray_node_facade: TMCSubarrayNodeFacade,
    csp: CSPFacade,
    event_tracer: TangoEventTracer,
):
    """Verify that the subarray transitions to the RESOURCING state."""
    (assert_that(event_tracer).described_as(
        f"Both TMC Subarray Node device ({subarray_node_facade.subarray_node})"
        f" and CSP Subarray device ({csp.csp_subarray}) "
        "ObsState attribute values should move to RESOURCING."
    ).within_timeout(ASSERTIONS_TIMEOUT)
    .have_events_occurred(
        (subarray_node_facade.subarray_node,
        "obsState",
        ObsState.RESOURCING,
        previous_value=context_fixt["starting_state"]),
        (csp.csp_subarray,
        "obsState",
        ObsState.RESOURCING,
        previous_value=context_fixt["starting_state"])
    ))



@then(parsers.parse("the subarray {subarray_id} should transition to the SCANNING state"))
def verify_scanning_state(context_fixt,
    subarray_id: str,
    subarray_node_facade: TMCSubarrayNodeFacade,
    csp: CSPFacade,
    event_tracer: TangoEventTracer,
):
    """Verify that the subarray transitions to the SCANNING state."""
    assert_that(event_tracer).described_as(
        f"Both TMC Subarray Node device ({subarray_node_facade.subarray_node})"
        f" and CSP Subarray device ({csp.csp_subarray}) "
        "ObsState attribute values should "
        "move from READY to SCANNING."
    ).within_timeout(ASSERTIONS_TIMEOUT)
    .have_events_occurred(
        (subarray_node_facade.subarray_node,
        "obsState",
        ObsState.SCANNING,
        previous_value=ObsState.READY),
        (csp.csp_subarray,
        "obsState",
        ObsState.SCANNING,
        previous_value=ObsState.READY)
    )




@then(parsers.parse("the subarray {subarray_id} should transition to the ABORTING state"))
def verify_aborting_state(context_fixt,
    subarray_id: str,
    subarray_node_facade: TMCSubarrayNodeFacade,
    csp: CSPFacade,
    event_tracer: TangoEventTracer,
):
    """Verify that the subarray transitions to the ABORTING state."""
    assert_that(event_tracer).described_as(
        f"Both TMC Subarray Node device ({subarray_node_facade.subarray_node})"
        f" and CSP Subarray device ({csp.csp_subarray}) "
        "ObsState attribute values should move to ABORTING."
    ).within_timeout(ASSERTIONS_TIMEOUT)
    .have_events_occurred(
        (subarray_node_facade.subarray_node,
        "obsState",
        ObsState.ABORTING,
        previous_value=context_fixt["starting_state"])
        (csp.csp_subarray,
        "obsState",
        ObsState.ABORTING,
        previous_value=context_fixt["starting_state"])
    )



@then(parsers.parse("the subarray {subarray_id} should transition to the CONFIGURING state"))
def verify_configuring_state(context_fixt,
    subarray_id: str,
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
    ).within_timeout(ASSERTIONS_TIMEOUT)
    .have_events_occurred(
        (subarray_node_facade.subarray_node,
        "obsState",
        ObsState.CONFIGURING,
        previous_value=ObsState.READY),
        (csp.csp_subarray,
        "obsState",
        ObsState.CONFIGURING,
        previous_value=ObsState.READY)
    )

@then(parsers.parse("the subarray {subarray_id} should transition to the IDLE state"))
def verify_idle_state(context_fixt,
    subarray_id: str,
    subarray_node_facade: TMCSubarrayNodeFacade,
    csp: CSPFacade,
    event_tracer: TangoEventTracer,
):
    """Verify that the subarray transitions to the IDLE state."""
    (assert_that(event_tracer).described_as(
        f"Both TMC Subarray Node device ({subarray_node_facade.subarray_node})"
        f" and CSP Subarray device ({csp.csp_subarray}) "
        "ObsState attribute values should move to IDLE from READY."
    ).within_timeout(ASSERTIONS_TIMEOUT)
    .have_events_occurred(
        (subarray_node_facade.subarray_node,
        "obsState",
        ObsState.IDLE,
        previous_value=ObsState.READY),
        (csp.csp_subarray,
        "obsState",
        ObsState.IDLE,
        previous_value=ObsState.READY)
    ))



@then(parsers.parse("the subarray {subarray_id} should transition to the READY state"))
def verify_ready_state(context_fixt,
    subarray_id: str,
    subarray_node_facade: TMCSubarrayNodeFacade,
    csp: CSPFacade,
    event_tracer: TangoEventTracer,
):
    """Verify that the subarray transitions to the READY state."""
    (assert_that(event_tracer).described_as(
        f"Both TMC Subarray Node device ({subarray_node_facade.subarray_node})"
        f" and CSP Subarray device ({csp.csp_subarray}) "
        "ObsState attribute values should move to READY from SCANNING."
    ).within_timeout(ASSERTIONS_TIMEOUT)
    .have_events_occurred(
        (subarray_node_facade.subarray_node,
        "obsState",
        ObsState.READY,
        previous_value=ObsState.SCANNING)
        (csp.csp_subarray,
        "obsState",
        ObsState.READY,
        previous_value=ObsState.SCANNING)
    ))


# TODO add the remaining THEN steps




