"""Verifies bug SKB-1013
"""
import pytest
from assertpy import assert_that
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


@pytest.mark.skb_918
@pytest.mark.batch1
@pytest.mark.SKA_mid
@scenario(
    "../tmc_new_ITH/features/skb_918_1013.feature",
    "Test abort command to verify skb-1013",
)
def test_verify_1013():
    """Test Configure command with and scan_type_id provided."""


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


@given("I assign resources to TMC Subarray")
def invoke_assign_resources(
    context_fixt: SubarrayTestContextData, tmc: TMCFacade
):
    """Invoke Assign Resources"""
    json_input = MyFileJSONInput(
        "centralnode", "assign_resources_mid"
    ).with_attribute("subarray_id", 1)

    context_fixt.when_action_result = tmc.assign_resources(
        json_input,
        wait_termination=True,
    )


@when("I invoke abort command on TMC Subarray")
def verify_abort_command_invoked(tmc: TMCFacade):
    """Invoke Abort command on TMC Subarray"""
    tmc.abort(wait_termination=True)


@then(
    "the commandCallInfo gets clear on SDP subarray mock device, "
    "preventing overflow issue"
)
def verify_command_call_info_cleared(
    sdp: SDPFacade, event_tracer: TangoEventTracer
):
    """Verify the commandCallInfo on SDP Mock device"""

    assert_that(event_tracer).within_timeout(
        ASSERTIONS_TIMEOUT
    ).has_change_event_occurred(sdp.sdp_subarray, "commandCallInfo", "[]")
