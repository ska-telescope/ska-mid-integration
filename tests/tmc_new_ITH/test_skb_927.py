"""Verifies bug SKB-927
"""

import json

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

from tests.resources.test_support.constant import (
    EVENT_DEFECT,
    RECEIVE_ADDRESSES,
    RESET_DEFECT,
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


@pytest.mark.batch1
@pytest.mark.SKA_mid
@scenario(
    "../tmc_new_ITH/features/skb_927.feature",
    "Test AssignResources with SDP v1.0 to verify fix for SKB-927",
)
def test_verify_927():
    """Test AssignResources with SDP v1.0."""


@given("subarray is in observation state EMPTY")
def subarray_in_idle_state(
    context_fixt: SubarrayTestContextData,
    tmc: TMCFacade,
    sdp: SDPFacade,
    csp: CSPFacade,
    event_tracer: TangoEventTracer,
    default_commands_inputs: TestHarnessInputs,
):
    """Ensure the subarray is in the IDLE state."""
    _setup_event_subscriptions(tmc, csp, sdp, event_tracer)
    context_fixt.starting_state = ObsState.IDLE
    sdp.sdp_subarray.SetDirectreceiveAddresses("{}")
    sdp.sdp_subarray.SetDefective(EVENT_DEFECT)
    sdp.sdp_subarray.SetDirectreceiveAddresses(RECEIVE_ADDRESSES)
    sdp.sdp_subarray.SetDefective(RESET_DEFECT)
    tmc.force_change_of_obs_state(
        ObsState.EMPTY,
        default_commands_inputs,
        wait_termination=True,
    )


@when("I assign resources with SDP interface v1.0 to the TMC Subarray")
def invoke_assign_resources(
    context_fixt: SubarrayTestContextData, tmc: TMCFacade
):
    """Invoke Assign Resources"""
    json_input = MyFileJSONInput(
        "centralnode", "assign_resources_mid"
    ).with_attribute("subarray_id", 1)
    assign_json = json_input.as_dict()
    assert (
        assign_json["sdp"]["interface"]
        == "https://schema.skao.int/ska-sdp-assignres/1.0"
    )
    context_fixt.when_action_result = tmc.assign_resources(
        json_input,
        wait_termination=True,
    )


@then(
    "AssignResources is successfully invoked on SDP with provided version v1.0"
)
def verify_version_sdp_mock_interface(sdp: SDPFacade):
    """Verify the interface version on SDP Mock device"""
    invoked_command_info = sdp.sdp_subarray.commandCallInfo
    latest_command_called, latest_command_input = invoked_command_info[-1]
    assert latest_command_called == "AssignResources"
    assert (
        json.loads(latest_command_input).get("interface")
        == "https://schema.skao.int/ska-sdp-assignres/1.0"
    )
