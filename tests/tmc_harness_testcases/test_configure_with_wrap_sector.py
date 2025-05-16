import json

import pytest
from assertpy import assert_that
from pytest_bdd import given, parsers, scenario, then, when
from ska_tango_base.control_model import ObsState
from ska_tango_testing.integration import TangoEventTracer, log_events
from tango import DevState

from tests.resources.test_harness.central_node_mid import CentralNodeWrapperMid
from tests.resources.test_harness.helpers import (
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
)
from tests.resources.test_harness.subarray_node import SubarrayNodeWrapper
from tests.resources.test_harness.utils.common_utils import JsonFactory
from tests.resources.test_support.constant import COMMAND_COMPLETED

TIMEOUT = 110


@pytest.mark.batch2
@pytest.mark.SKA_mid
@scenario(
    "../features/xtp-81402.feature",
    "TMC behavior when configure command is invoked with wrap_sector",
)
def test_tmc_configure_with_wrap_sector_key():
    """
    Test case to verify Configure functionality with wrap_sector key.
    """


@given("a TMC")
def given_tmc(
    central_node_mid: CentralNodeWrapperMid,
    subarray_node: SubarrayNodeWrapper,
    event_tracer: TangoEventTracer,
):
    """Given a TMC"""
    # Setting up subscriptions
    event_tracer.subscribe_event(
        central_node_mid.central_node, "telescopeState"
    )
    event_tracer.subscribe_event(
        central_node_mid.central_node, "longRunningCommandResult"
    )
    event_tracer.subscribe_event(subarray_node.subarray_node, "obsState")
    event_tracer.subscribe_event(
        subarray_node.subarray_node, "longRunningCommandResult"
    )

    # Logging setup
    log_events(
        {
            central_node_mid.central_node: [
                "telescopeState",
                "longRunningCommandResult",
            ],
            subarray_node.subarray_node: [
                "obsState",
                "longRunningCommandResult",
            ],
        }
    )
    # TelescopeOn
    central_node_mid.move_to_on()

    # Assertions
    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION AFTER ON COMMAND: "
        "Central Node device"
        f"({central_node_mid.central_node.dev_name()}) "
        "is expected to be in TelescopeState ON",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_mid.central_node,
        "telescopeState",
        DevState.ON,
    )
    assert_that(event_tracer).described_as(
        "FAILED UNEXPECTED INITIAL OBSSTATE: "
        "Subarray Node device"
        f"({central_node_mid.subarray_node.dev_name()}) "
        "is expected to be in EMPTY obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_mid.subarray_node,
        "obsState",
        ObsState.EMPTY,
    )
    event_tracer.clear_events()


@when("the resources are assigned to TMC SubarrayNode")
def move_subarray_node_to_idle_obsstate(
    central_node_mid: CentralNodeWrapperMid,
    event_tracer: TangoEventTracer,
    command_input_factory: JsonFactory,
    subarray_node: SubarrayNodeWrapper,
) -> None:
    """Move TMC Subarray to IDLE obsstate."""
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_mid", command_input_factory
    )
    _, pytest.unique_id = central_node_mid.store_resources(assign_input_json)

    event_tracer.subscribe_event(subarray_node.subarray_node, "obsState")
    event_tracer.subscribe_event(
        central_node_mid.central_node, "longRunningCommandResult"
    )

    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        "'the subarray must be in the IDLE obsState'"
        "TMC Subarray device"
        f"({subarray_node.subarray_node.dev_name()}) "
        "is expected to be in IDLE obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.IDLE,
    )
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        "'the subarray is in IDLE obsState'"
        "TMC Central Node device"
        f"({central_node_mid.central_node.dev_name()}) "
        "is expected have longRunningCommand as"
        '(unique_id,(ResultCode.OK,"Command Completed"))',
    ).within_timeout(60).has_change_event_occurred(
        central_node_mid.central_node,
        "longRunningCommandResult",
        (pytest.unique_id[0], COMMAND_COMPLETED),
    )
    event_tracer.clear_events()


@when(
    parsers.parse(
        "I execute configure json {configure_json} {conf_type}"
        " with wrap_sector {wrap_sector}"
    )
)
def when_i_execute_configure_json_with_provided_wrap_sector(
    subarray_node,
    event_tracer,
    command_input_factory,
    configure_json,
    wrap_sector,
    conf_type,
):
    """
    Invokes Configure command on TMC SubarrayNode
    """
    configure_input_json = prepare_json_args_for_commands(
        configure_json, command_input_factory
    )
    configure_data = json.loads(configure_input_json)
    configure_data["pointing"]["wrap_sector"] = wrap_sector
    if conf_type == "without_receptors":
        del configure_data["pointing"]["groups"][0]["receptors"]
    pytest.wrap_sector = wrap_sector
    pytest.command_result = subarray_node.execute_transition(
        "Configure", argin=json.dumps(configure_data)
    )
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        "'the subarray must be in the CONFIGURING obsState'"
        "TMC Subarray device"
        f"({subarray_node.subarray_node.dev_name()}) "
        "is expected to be in CONFIGURING obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.CONFIGURING,
    )


@then("the TMC SubarrayNode transitions to obsState READY")
def verify_ready_obsstate(
    subarray_node: SubarrayNodeWrapper,
    event_tracer: TangoEventTracer,
) -> None:
    """This step in test case ensure subarray node is in Obsstate READY"""
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        "'the subarray must be in the READY obsState'"
        "TMC Subarray device"
        f"({subarray_node.subarray_node.dev_name()}) "
        "is expected to be in READY obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.READY,
    )

    # Verify wrap_sector is applied as expected on dish leaf node.
    for dish_pointing_device in subarray_node.dish_pointing_device_proxy_list:
        program_track_table = json.loads(
            dish_pointing_device.pointingprogramtracktable
        )
        dpd_target_data = json.loads(dish_pointing_device.targetdata)
        assert (
            int(pytest.wrap_sector)
            == dpd_target_data["pointing"]["wrap_sector"]
        )
        # Assert azimuth value getting updated as per value of wrap_sector
        if not int(pytest.wrap_sector):
            assert program_track_table[1] > 0
        else:
            assert program_track_table[1] < 0
    event_tracer.clear_events()
