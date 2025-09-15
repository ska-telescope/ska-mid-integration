"""Verifies bug SKB-918
"""
import json

import pytest
from assertpy import assert_that
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState
from ska_integration_test_harness.facades.csp_facade import CSPFacade
from ska_integration_test_harness.facades.sdp_facade import SDPFacade
from ska_integration_test_harness.facades.tmc_facade import TMCFacade
from ska_integration_test_harness.inputs.json_input import DictJSONInput
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
    "../tmc_new_ITH/features/skb_918.feature",
    "Test Configure command to verify skb-918",
)
def test_verify_918():
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


@given(
    parsers.parse(
        "I assign resources with scan_type_id {scan_type_id} to TMC Subarray"
    )
)
def invoke_assign_resources(
    context_fixt: SubarrayTestContextData, tmc: TMCFacade, scan_type_id: str
):
    """Invoke Assign Resources"""
    json_input = MyFileJSONInput(
        "centralnode", "assign_resources_mid"
    ).with_attribute("subarray_id", 1)
    assign_json = json.loads(json_input.as_str())
    assign_json["sdp"]["execution_block"]["scan_types"][1][
        "scan_type_id"
    ] = scan_type_id

    context_fixt.when_action_result = tmc.assign_resources(
        DictJSONInput(assign_json),
        wait_termination=True,
    )


@when(
    parsers.parse(
        "I invoke configure command with "
        "scan_type_id {scan_type_id} on TMC Subarray"
    )
)
def verify_version_sdp_mock_interface(
    tmc: TMCFacade, scan_type_id: str, context_fixt: SubarrayTestContextData
):
    """Verify the scan_type_id on SDP Mock device"""
    json_input = MyFileJSONInput("subarray", "command_Configure")
    configure_json = json.loads(json_input.as_str())
    configure_json["sdp"]["scan_type"] = scan_type_id
    context_fixt.when_action_result = tmc.configure(
        DictJSONInput(configure_json),
        wait_termination=False,
    )


@then(
    "mock SDP subarray mock successfully executes the "
    "Configure command and goes to READY obsstate"
)
def verify_ready_state(
    context_fixt: SubarrayTestContextData,
    tmc: TMCFacade,
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
    context_fixt.starting_state = ObsState.CONFIGURING
    assert_that(event_tracer).described_as(
        f"Both TMC Subarray Node device ({tmc.subarray_node})"
        f", CSP Subarray device ({csp.csp_subarray}) "
        f"and SDP Subarray device ({sdp.sdp_subarray}) "
        "ObsState attribute values should move "
        f"from {str(context_fixt.starting_state)} to READY."
    ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
        tmc.subarray_node,
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
    context_fixt.starting_state = ObsState.READY
