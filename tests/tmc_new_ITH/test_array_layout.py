"""Verifies scan functionality
"""

import json

import pytest
import tango
from assertpy import assert_that
from pytest_bdd import given, scenario, then, when
from ska_control_model import ObsState, ResultCode
from ska_integration_test_harness.facades.csp_facade import CSPFacade
from ska_integration_test_harness.facades.sdp_facade import SDPFacade
from ska_integration_test_harness.facades.tmc_facade import TMCFacade
from ska_tango_testing.integration import TangoEventTracer, log_events

from tests.conftest import LOGGER
from tests.resources.test_harness.helpers import (
    calculate_epoch_difference,
    generate_ska_epoch_tai_value,
    wait_till_delay_values_are_populated,
)
from tests.resources.test_harness.subarray_node import SubarrayNodeWrapper
from tests.tmc_csp_new_ITH.conftest import (  # SubarrayTestContextData,
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
):
    """
    Execute the first AssignResources command which should succeed.
    """
    _setup_event_subscriptions(tmc, csp, sdp, event_tracer)
    json_input = MyFileJSONInput(
        "centralnode", "assign_resources_array_layout"
    )
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


@when("I invoke the Configure command on the SubarrayNode")
def verify_version_sdp_mock_interface(
    tmc: TMCFacade,
    context_fixt: SubarrayTestContextData,
    event_tracer: TangoEventTracer,
    csp,
    sdp,
):
    """Invoke Configure command on SubarrayNode."""
    json_input = MyFileJSONInput("subarray", "command_Configure")
    context_fixt.when_action_result = tmc.configure(
        json_input,
        wait_termination=False,
    )
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


@then(
    "the DLN targetData attribute is updated using the array layout "
    "from Telmodel"
)
def then_dln_target_data_updated():

    """Verify that the DLN targetData attribute is updated."""
    # This is verified in the DPDA test, so no need to re-verify here.
    dpd = tango.DeviceProxy("mid-tmc/dish-pointing/ska001")
    target_data = json.loads(dpd.targetData)
    LOGGER.info(f"DPD targetData attribute: {target_data}")
    assert "array_layout" in target_data

    array_layout = target_data["array_layout"]

    # 2. Validate schema interface version
    assert (
        array_layout.get("interface")
        == "https://schema.skao.int/ska-telmodel-layout-receptor/1.1"
    ), "Unexpected array_layout interface version"

    # 3. Validate dish/station identity
    assert array_layout.get("station_label") == "SKA001"
    assert array_layout.get("station_id") == 65


@then(
    "CSP Subarray Leaf Node starts generating delay values with proper epoch"
)
def check_if_delay_values_are_generating(
    subarray_node: SubarrayNodeWrapper,
) -> None:
    """Check if delay values are generating."""
    ska_epoch_tai = generate_ska_epoch_tai_value()
    LOGGER.info(f"ska_epoch_tai : {ska_epoch_tai}")
    delay_json, delay_generated_time = wait_till_delay_values_are_populated(
        subarray_node.csp_subarray_leaf_node
    )
    LOGGER.info(f"delay_json: {delay_json}")
    LOGGER.info(f"delay_generated_time: {delay_generated_time}")
    epoch_difference = calculate_epoch_difference(
        delay_generated_time, ska_epoch_tai, delay_json
    )
    LOGGER.info(f"epoch_difference: {epoch_difference}")
    assert epoch_difference < 30
