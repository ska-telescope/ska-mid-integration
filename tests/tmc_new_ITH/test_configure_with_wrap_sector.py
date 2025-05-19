"""Test case to verify wrap_sector gets applied as expected
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

# from tests.tmc_new_ITH.utils.dpd_facade import DishPointingDeviceFacade
from tests.tmc_new_ITH.utils.dpd_facade import DishPointingDeviceFacade

# from tests.tmc_new_ITH.utils.utils import setup_event_subscriptions


@pytest.mark.batch1
@pytest.mark.t1
@pytest.mark.SKA_mid
@scenario(
    "../tmc_new_ITH/features/xtp_81402_configure_with_wrap_sector.feature",
    "TMC behavior when configure command is invoked with wrap_sector",
)
def test_verify_wrap_sector_with_main_configure_json():
    """Test TMC can handle wrap_sector with any kind on main configure json"""


@given("a TMC")
def given_a_tmc(
    tmc: TMCFacade,
    sdp: SDPFacade,
    csp: CSPFacade,
    event_tracer: TangoEventTracer,
):
    """Given a TMC"""
    # setup_event_subscriptions(tmc, csp, sdp, event_tracer)


@when("the resources are assigned to TMC SubarrayNode")
def subarray_in_idle_state(
    context_fixt: SubarrayTestContextData,
    tmc: TMCFacade,
    sdp: SDPFacade,
    csp: CSPFacade,
    event_tracer: TangoEventTracer,
    default_commands_inputs: TestHarnessInputs,
):
    """Ensure the subarray is in the IDLE state."""
    context_fixt.starting_state = ObsState.EMPTY
    tmc.force_change_of_obs_state(
        ObsState.IDLE,
        TestHarnessInputs(
            assign_input=MyFileJSONInput(
                "centralnode", "assign_resources_mid"
            ),
            configure_input=MyFileJSONInput(
                "subarray", "configure_holography_adr106"
            ),
        ),
        wait_termination=True,
    )


@when(
    parsers.parse(
        "I execute configure json {configure_json} {conf_type}"
        " with wrap_sector {wrap_sector}"
    )
)
def when_i_execute_configure_json_with_provided_wrap_sector(
    context_fixt: SubarrayTestContextData,
    tmc: TMCFacade,
    configure_json: str,
    conf_type: str,
    wrap_sector: int,
):
    """Invoke Configure command with wrap_sector key"""
    json_input = MyFileJSONInput("subarray", configure_json)
    configure_data = json.loads(json_input.as_str())
    configure_data["pointing"]["wrap_sector"] = wrap_sector
    if conf_type == "without_receptors":
        del configure_data["pointing"]["groups"][0]["receptors"]
    context_fixt.when_action_result = tmc.configure(
        DictJSONInput(configure_data), wait_termination=True
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


@then("provided {wrap_sector} is applied on dish leaf node")
def verify_configuration_data(
    context_fixt: SubarrayTestContextData,
    tmc: TMCFacade,
    dish_pointng_devices: DishPointingDeviceFacade,
    wrap_sector,
):
    """Verify that configuration data is applied correctly on dishes"""

    for dpd_name in dish_pointng_devices.dish_pointing_device_dict.keys():
        dpd = dish_pointng_devices.dish_pointing_device_dict[dpd_name]
        program_track_table = json.loads(dpd.pointingprogramtracktable)
        dpd_target_data = json.loads(dpd.targetdata)
        assert int(wrap_sector) == dpd_target_data["pointing"]["wrap_sector"]
        # Assert azimuth value getting updated as per value of wrap_sector
        if not int(wrap_sector):
            assert program_track_table[1] > 0
        else:
            assert program_track_table[1] < 0
