"""Verifies bug SKB-617
"""

# import json

import pytest
from pytest_bdd import given, scenario, then, when
from ska_control_model import ObsState
from ska_integration_test_harness.facades.csp_facade import CSPFacade
from ska_integration_test_harness.facades.sdp_facade import SDPFacade
from ska_integration_test_harness.facades.tmc_facade import TMCFacade
from ska_integration_test_harness.inputs.test_harness_inputs import (
    TestHarnessInputs,
)
from ska_tango_testing.integration import TangoEventTracer, log_events

from tests.resources.test_harness.helpers import (
    check_for_device_command_event_tracer,
)
from tests.tmc_csp_new_ITH.conftest import SubarrayTestContextData
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

    event_tracer.subscribe_event(tmc.central_node, "longRunningCommandResult")
    event_tracer.subscribe_event(tmc.subarray_node, "longRunningCommandResult")

    log_events(
        {
            tmc.subarray_node: [
                "obsState",
                "longRunningCommandResult",
            ],
            tmc.central_node: ["longRunningCommandResult"],
        },
        event_enum_mapping={"obsState": ObsState},
    )


# @pytest.mark.batch1
@pytest.mark.test
@pytest.mark.SKA_mid
@scenario(
    "../tmc_new_ITH/features/skb_617.feature",
    "Test AssignResources with empty SDP block",
)
def test_verify_617():
    """Test AssignResources with empty SDP block to verify SKB-617 fix."""


@given("subarray is in observation state EMPTY")
def subarray_in_empty_state(
    context_fixt: SubarrayTestContextData,
    tmc: TMCFacade,
    sdp: SDPFacade,
    csp: CSPFacade,
    event_tracer: TangoEventTracer,
    default_commands_inputs: TestHarnessInputs,
):
    """Ensure the subarray is in the EMPTY state."""
    _setup_event_subscriptions(tmc, csp, sdp, event_tracer)
    context_fixt.starting_state = ObsState.EMPTY
    tmc.force_change_of_obs_state(
        ObsState.EMPTY,
        default_commands_inputs,
        wait_termination=True,
    )

@when("I invoke assign resources with empty SDP block")
def invoke_assign_resources(context_fixt: SubarrayTestContextData, tmc: TMCFacade):
    """Invoke Assign Resources"""
    json_input = (
        MyFileJSONInput("centralnode", "assign_resources_mid")
        .with_attribute("subarray_id", 1)
        .with_attribute("sdp", {})  # Setting SDP directly in the input object
    )

    context_fixt.when_action_result = tmc.assign_resources(
        json_input, 
        wait_termination=True,
    )

# @when("I invoke assign resources with empty SDP block")
# def invoke_assign_resources(
#     context_fixt: SubarrayTestContextData, tmc: TMCFacade
# ):
#     """Invoke Assign Resources"""
#     json_input = MyFileJSONInput(
#         "centralnode", "assign_resources_mid"
#     ).with_attribute("subarray_id", 1)
#     assign_json = json_input.as_dict()
#     assign_json["sdp"] = {}
#     context_fixt.when_action_result = tmc.assign_resources(
#         assign_json,
#         wait_termination=True,
#     )
#     # json_input = json.dumps(assign_json)
#     # context_fixt.when_action_result = tmc.assign_resources(
#     #     json_input,
#     #     wait_termination=True,
#     # )


@then("AssignResources is successfully invoked on TMC")
def verify_version_tmc_in_idle(tmc: TMCFacade, event_tracer: TangoEventTracer):
    """Verify the AssignResources command was invoked on TMC."""
    assert check_for_device_command_event_tracer(
        tmc.subarray_node,
        "obsState",
        ObsState.IDLE,
        event_tracer,
        "AssignResources",
    )
