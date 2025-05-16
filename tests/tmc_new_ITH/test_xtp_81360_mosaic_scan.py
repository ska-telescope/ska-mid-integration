"""Test case to verify fixed trajectory works as expected
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
from ska_tango_testing.integration import TangoEventTracer

from tests.tmc_csp_new_ITH.conftest import (
    ASSERTIONS_TIMEOUT,
    SubarrayTestContextData,
)
from tests.tmc_csp_new_ITH.utils.my_file_json_input import MyFileJSONInput
from tests.tmc_new_ITH.utils.utils import setup_event_subscriptions


@pytest.mark.batch1
@pytest.mark.test
@pytest.mark.SKA_mid
@scenario(
    "../tmc_new_ITH/features/xtp_81360_mosiac_scan.feature",
    "TMC Mid execute mosiac scan",
)
def test_verify_mosiac_scan():
    """Test TMC perform mosaic scan with changing offsets provided in
    partial configuration.
    """


@given("TMC Subarray is in observation state IDLE")
def subarray_in_idle_state(
    context_fixt: SubarrayTestContextData,
    tmc: TMCFacade,
    sdp: SDPFacade,
    csp: CSPFacade,
    event_tracer: TangoEventTracer,
    default_commands_inputs: TestHarnessInputs,
):
    """Ensure the subarray is in the IDLE state."""
    setup_event_subscriptions(tmc, csp, sdp, event_tracer)
    context_fixt.starting_state = ObsState.IDLE

    tmc.force_change_of_obs_state(
        ObsState.IDLE,
        default_commands_inputs,
        wait_termination=True,
    )


@given("a subarray configured for a mosaic scan with multiple groups")
def subarray_configured_with_multiple_groups(
    context_fixt: SubarrayTestContextData,
    tmc: TMCFacade,
    sdp: SDPFacade,
    csp: CSPFacade,
    event_tracer: TangoEventTracer,
    default_commands_inputs: TestHarnessInputs,
):
    """Ensure the subarray is configured with multiple groups
    and obs state is changed to READY
    """
    context_fixt.when_action_name = "Configure"

    json_input = MyFileJSONInput("subarray", "configure_holography_adr106")

    context_fixt.when_action_result = tmc.configure(
        json_input,
        wait_termination=False,
    )


@then(
    "the subarray executes the commands successfully and is in READY obsState"
)
@given("the subarray is in READY obsState")
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


@when(
    parsers.parse(
        "I perform partial configurations with "
        "{x_offsets} {y_offsets} offsets followed by scans"
    )
)
def send_partial_configure_command(
    context_fixt: SubarrayTestContextData,
    tmc: TMCFacade,
    x_offsets: list,
    y_offsets: list,
):
    """
    This steps execute multiple partial configuration for each x, y offsets
    provided in x offsets and y offsets list
    """
    context_fixt.when_action_name = "Configure"
    json_input = MyFileJSONInput("subarray", "partial_configure_trajectory")
    x_offset_list = x_offsets.split(",")
    y_offset_list = y_offsets.split(",")
    for x, y in zip(x_offset_list, y_offset_list):
        partial_configure_json = json.loads(json_input.as_str())
        partial_configure_json["pointing"]["groups"][0]["trajectory"][
            "attrs"
        ] = {
            "x": float(x),
            "y": float(y),
        }
        context_fixt.when_action_result = tmc.configure(
            DictJSONInput(partial_configure_json), wait_termination=True
        )
        # TODO add assert for targetData
