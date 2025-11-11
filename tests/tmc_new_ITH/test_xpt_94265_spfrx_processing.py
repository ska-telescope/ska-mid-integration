"""Test case to verify configure command with SPFRx parameters
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

from tests.resources.test_support.constant import (
    expected_json_spfrx_param_case_all_different,
    expected_json_spfrx_param_case_all_dishes,
    expected_json_spfrx_param_case_multiple_dish_same_parameter,
    expected_json_spfrx_param_case_single_parameter_per_dish,
)
from tests.tmc_csp_new_ITH.conftest import (
    ASSERTIONS_TIMEOUT,
    SubarrayTestContextData,
)
from tests.tmc_csp_new_ITH.utils.my_file_json_input import MyFileJSONInput
from tests.tmc_new_ITH.utils.utils import setup_event_subscriptions


def update_configuration_json(config_json: dict, config_data: str):
    """Update config json based on config case provided
    Args:
        config_json(dict): Json for partial configuration
        config_data(str): type of data to add/update
    """
    match config_data:
        case "configuration_with_all_dish":
            config_json["dish"][
                "spfrx_processing_parameters"
            ] = expected_json_spfrx_param_case_all_dishes["dish"][
                "spfrx_processing_parameters"
            ]
        case "configuration_with_single_parameter_per_dish":
            config_json["dish"][
                "spfrx_processing_parameters"
            ] = expected_json_spfrx_param_case_single_parameter_per_dish[
                "dish"
            ][
                "spfrx_processing_parameters"
            ]
        case "configuration_with_multiple_dish_same_parameter":
            config_json["dish"][
                "spfrx_processing_parameters"
            ] = expected_json_spfrx_param_case_multiple_dish_same_parameter[
                "dish"
            ][
                "spfrx_processing_parameters"
            ]
        case "configuration_with_all_different":
            config_json["dish"][
                "spfrx_processing_parameters"
            ] = expected_json_spfrx_param_case_all_different["dish"][
                "spfrx_processing_parameters"
            ]
        case _:
            raise ValueError(f"Unknown configuration data type: {config_data}")


@pytest.mark.batch1
@pytest.mark.SKA_mid
@scenario(
    "../tmc_new_ITH/features/xtp_94265_spfrx_processing.feature",
    "TMC Behaviour when SPFRx configuration is provided",
)
def test_spfrx_configuration():
    """Test TMC  configuration when SPFRx  configuration provided"""


@given("a TMC")
def given_a_tmc(
    tmc: TMCFacade,
    sdp: SDPFacade,
    csp: CSPFacade,
    event_tracer: TangoEventTracer,
):
    """Given a TMC"""
    setup_event_subscriptions(tmc, csp, sdp, event_tracer)


@given("TMC SubarrayNode is in IDLE ObsState")
def subarray_in_ready_state(
    context_fixt: SubarrayTestContextData,
    tmc: TMCFacade,
):
    """Ensure the subarray is in the IDLE state."""
    context_fixt.starting_state = ObsState.EMPTY
    tmc.force_change_of_obs_state(
        ObsState.IDLE,
        TestHarnessInputs(
            assign_input=MyFileJSONInput("centralnode", "assign_resources_mid")
        ),
        wait_termination=True,
    )


@when(
    parsers.parse(
        "I execute configure command with SPFRx {configuration_data}"
    )
)
def send_partial_configure_command(
    context_fixt: SubarrayTestContextData,
    tmc: TMCFacade,
    configuration_data: str,
):
    """Update configuration json as per configuration data
    and execute configure command
    """
    json_input = MyFileJSONInput("subarray", "Configure_band5_dc")
    config_json = json.loads(json_input.as_str())
    update_configuration_json(config_json, configuration_data)
    pytest.configuration_data = configuration_data
    context_fixt.when_action_result = tmc.configure(
        DictJSONInput(config_json), wait_termination=True
    )


@then("the TMC SubarrayNode transitions to obsState READY")
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
