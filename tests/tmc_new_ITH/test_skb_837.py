"""Verify bug SKB-837
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


@pytest.mark.batch1
@pytest.mark.SKA_mid
@scenario(
    "../tmc_new_ITH/features/skb_837_receive_addresses_event_missing.feature",
    "Fallback to attribute‑read when no change event for attribute"
    " receiveAddresses",
)
def test_verify_837():
    """Test Configure comannd when receive addresses event is missing."""


@given("subarray is in observation state IDLE")
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

    json_input = MyFileJSONInput(
        "centralnode", "assign_resources_mid"
    ).with_attribute("subarray_id", 1)

    context_fixt.when_action_result = tmc.assign_resources(
        json_input,
        wait_termination=True,
    )


@given("change event data is EMPTY for attribute receiveAddresses")
def change_event_is_empty(sdp: SDPFacade, event_tracer: TangoEventTracer):
    """Verifies that the change event of attribute receiveAddresses is EMPTY.

    :param sdp: sdp device facade instance
    :type sdp: SDPFacade
    :param event_tracer: TanogEventTracer object to handle events.
    :type event_tracer: TangoEventTracer
    """
    assert_that(event_tracer).described_as(
        "SDP subarry "
        f"({sdp.sdp_subarray}) "
        "is expected to report the"
        "receiveAddresses as EMPTY"
    ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
        sdp.sdp_subarray,
        "receiveAddresses",
        "{}",
    )


@when("I configure the subarray")
def send_configure_command(
    context_fixt: SubarrayTestContextData,
    tmc: TMCFacade,
):
    """
    Send the Configure command to the subarray.

    This step uses the tmc to send a Configure command
    to the specified subarray. It uses a pre-defined JSON input file and
    sends the command without waiting for termination. The action result
    is stored in the context fixture.
    """
    context_fixt.when_action_name = "Configure"

    json_input = MyFileJSONInput("subarray", "configure_mid")

    context_fixt.when_action_result = tmc.configure(
        json_input,
        wait_termination=False,
    )


@then("Subarray transitions to observation state READY")
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
