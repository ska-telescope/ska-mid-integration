"""Verifies scan functionality
"""

import json

import pytest
from assertpy import assert_that
from pytest_bdd import given, scenario, then, when
from ska_control_model import ObsState, ResultCode
from ska_integration_test_harness.facades.csp_facade import CSPFacade
from ska_integration_test_harness.facades.sdp_facade import SDPFacade
from ska_integration_test_harness.facades.tmc_facade import TMCFacade
from ska_integration_test_harness.inputs.test_harness_inputs import (
    TestHarnessInputs,
)
from ska_tango_testing.integration import TangoEventTracer, log_events

from tests.conftest import LOGGER
from tests.tmc_csp_new_ITH.conftest import (
    ASSERTIONS_TIMEOUT,
    SubarrayTestContextData,
)
from tests.tmc_csp_new_ITH.utils.my_file_json_input import MyFileJSONInput


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
    event_tracer.subscribe_event(sdp.sdp_subarray, "receiveAddresses")
    event_tracer.subscribe_event(sdp.sdp_subarray, "commandCallInfo")
    event_tracer.subscribe_event(tmc.central_node, "longRunningCommandResult")
    event_tracer.subscribe_event(tmc.subarray_node, "longRunningCommandResult")

    log_events(
        {
            tmc.subarray_node: [
                "obsState",
                "longRunningCommandResult",
            ],
            csp.csp_subarray: ["obsState"],
            sdp.sdp_subarray: [
                "obsState",
                "commandCallInfo",
                "receiveAddresses",
            ],
            tmc.central_node: ["longRunningCommandResult"],
        },
        event_enum_mapping={"obsState": ObsState},
    )


@pytest.mark.batch12
@pytest.mark.SKA_mid
@scenario(
    "../tmc_new_ITH/features/array_layout.feature",
    "Verify array layout functionality in TMC mid",
)
def test_verify_array_layout_functionality():
    """Test array layout functionality."""


@given(
    "AssignResources is invoked on the SubarrayNode with an "
    "arrayLayoutUri so that the SN.arrayLayoutUri attribute is updated"
)
def given_assign_resources_executed_successfully(
    tmc: TMCFacade,
    sdp: SDPFacade,
    csp: CSPFacade,
    event_tracer: TangoEventTracer,
    default_commands_inputs: TestHarnessInputs,
    receptor1: str,
    subarray_id: str,
):
    """
    Execute the first AssignResources command which should succeed.
    """
    _setup_event_subscriptions(tmc, csp, sdp, event_tracer)
    json_input = MyFileJSONInput(
        "centralnode", "assing_resources_array_layout"
    ).with_attribute("subarray_id", subarray_id)

    _, pytest.unique_id = tmc.assign_resources(json_input)

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


@when("I invoke the Configure command on the SubarrayNode")
def verify_version_sdp_mock_interface(
    tmc: TMCFacade, context_fixt: SubarrayTestContextData
):
    """Invoke Configure command on SubarrayNode."""
    json_input = MyFileJSONInput("subarray", "command_Configure")
    context_fixt.when_action_result = tmc.configure(
        json_input,
        wait_termination=False,
    )


@then(
    "the DLN targetData attribute is updated using the array layout "
    "referenced by SN.arrayLayoutUri"
)
def then_dln_target_data_updated(
    tmc: TMCFacade,
):
    """Verify that DLN targetData attribute is updated correctly."""
    initial_resources = (
        tmc.dish_leaf_node_list[0].read_attribute("targetData").value
    )
    LOGGER.info(f"DLN targetData attribute: {initial_resources}")
