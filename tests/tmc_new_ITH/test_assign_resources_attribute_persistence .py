"""Test case to verify AssignedResources attribute persistence after failed
AssignResources."""

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
from ska_tango_testing.integration import TangoEventTracer
from ska_tango_testing.mock.placeholders import Anything

from tests.resources.test_support.constant import FAILED_RESULT_DEFECT
from tests.tmc_csp_new_ITH.utils.my_file_json_input import MyFileJSONInput
from tests.tmc_new_ITH.conftest import ASSERTIONS_TIMEOUT
from tests.tmc_new_ITH.utils.utils import setup_event_subscriptions


@pytest.mark.batch2
@pytest.mark.SKA_mid
@scenario(
    "../tmc_new_ITH/features/"
    + "subarray_assignresources_attribute_persistence.feature",
    "AssignedResources attribute persists after failed second AssignResources",
)
def test_assign_resources_attribute_persistence():
    """Test that verifies the AssignedResources attribute maintains its state
    when a subsequent AssignResources command fails.
    """
    pass


@given("a TMC")
def given_tmc(
    tmc: TMCFacade,
    sdp: SDPFacade,
    csp: CSPFacade,
    event_tracer: TangoEventTracer,
):
    """
    Initialize the TMC and verify its state.
    """
    setup_event_subscriptions(tmc, csp, sdp, event_tracer)

    assert_that(event_tracer).described_as(
        "TMC telescope device telescopeState should be ON"
    ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
        tmc.central_node, "telescopeState", "ON"
    )

    assert_that(event_tracer).described_as(
        "TMC subarray obsState should be EMPTY"
    ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
        tmc.subarray_node, "obsState", ObsState.EMPTY
    )

    event_tracer.clear_events()


@given(
    parsers.parse(
        "AssignResources is executed successfully"
        " on SubarrayNode {subarray_id}"
    )
)
def given_assign_resources_executed_successfully(
    tmc: TMCFacade,
    sdp: SDPFacade,
    csp: CSPFacade,
    event_tracer: TangoEventTracer,
    default_commands_inputs: TestHarnessInputs,
    subarray_id: str,
):
    """
    Execute the first AssignResources command which should succeed.
    """

    assign_input = MyFileJSONInput(
        "centralnode", "incremental_assign_resources_01"
    )
    _, pytest.unique_id = tmc.assign_resources(assign_input)

    assert_that(event_tracer).described_as(
        "TMC subarray obsState should move to IDLE"
    ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
        tmc.subarray_node, "obsState", ObsState.IDLE
    )

    assert_that(event_tracer).described_as(
        "AssignResources command should complete successfully"
    ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
        tmc.central_node,
        "longRunningCommandResult",
        (
            pytest.unique_id[0],
            json.dumps(((ResultCode.OK), "Command Completed")),
        ),
    )

    event_tracer.clear_events()


@given(
    "the AssignedResources attribute is updated with first assigned resources"
)
def verify_first_assigned_resources(tmc: TMCFacade):
    """
    Store the initial AssignedResources for later comparison.
    """
    initial_resources = tmc.subarray_node.read_attribute(
        "assignedResources"
    ).value
    assert_that(initial_resources).described_as(
        "AssignedResources should not be empty after first assignment"
    ).is_not_none()

    # Store for later comparison
    pytest.first_assigned_resources = initial_resources


@when(
    parsers.parse(
        "I execute second AssignResources command"
        " on SubarrayNode {subarray_id} that fails"
    )
)
def execute_second_assign_resources_fail(
    tmc: TMCFacade,
    sdp: SDPFacade,
    csp: CSPFacade,
    event_tracer: TangoEventTracer,
    default_commands_inputs: TestHarnessInputs,
    subarray_id: str,
):
    """
    Execute the second AssignResources command which should fail.
    """
    assign_input = MyFileJSONInput(
        "centralnode", "incremental_assign_resources_02"
    )
    csp.csp_subarray.SetDefective(FAILED_RESULT_DEFECT)
    _, pytest.unique_id = tmc.assign_resources(assign_input)

    assert_that(event_tracer).described_as(
        "TMC subarray obsState should remain in IDLE"
    ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
        tmc.subarray_node, "obsState", ObsState.IDLE
    )

    assert_that(event_tracer).described_as(
        "AssignResources command should fail"
    ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
        tmc.central_node,
        "longRunningCommandResult",
        (pytest.unique_id[0], Anything),
    )
    # reset the defect
+   csp.csp_subarray.SetDefective(json.dumps({"enabled": False}))

    event_tracer.clear_events()


@then(
    "the AssignedResources attribute"
    " should retain the first assigned resources"
)
def verify_assigned_resources_unchanged(tmc: TMCFacade):
    """
    Verify that the AssignedResources attribute still
    contains the first assignment.
    """

    current_resources = tmc.subarray_node.read_attribute(
        "assignedResources"
    ).value
    assert_that(current_resources).described_as(
        "AssignedResources should match the initial assignment"
    ).is_equal_to(pytest.first_assigned_resources)


@then("the subarray should remain in IDLE state")
def verify_subarray_state(tmc: TMCFacade):
    """
    Verify that the subarray remains in IDLE state.
    """
    current_state = tmc.subarray_node.read_attribute("obsState").value
    assert_that(current_state).described_as(
        "Subarray should remain in IDLE state"
    ).is_equal_to(ObsState.IDLE)
