import json

import pytest
from assertpy import assert_that
from pytest_bdd import given, parsers, scenario, then, when
from ska_tango_base.control_model import ObsState
from ska_tango_testing.integration import TangoEventTracer, log_events
from tango import DevState

from tests.conftest import LOGGER
from tests.resources.test_harness.central_node_mid import CentralNodeWrapperMid
from tests.resources.test_harness.constant import COMMAND_COMPLETED
from tests.resources.test_harness.helpers import (
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
)
from tests.resources.test_harness.subarray_node import SubarrayNodeWrapper
from tests.resources.test_harness.utils.common_utils import JsonFactory
from tests.resources.test_support.common_utils.result_code import ResultCode


@scenario(
    "../features/successful_scan_after_failed_configure.feature",
    "Successfully execute a scan after a failed attempt to configure",
)
def test_configure_resource_with_invalid_json():
    """
    Test Configure command with input as invalid json.
    """


@given(
    parsers.parse(
        "a subarray {subarray_id} with resources {resources_list} in obsState IDLE"  # noqa: E501
    )
)
def given_tmc(
    command_input_factory: JsonFactory,
    event_tracer: TangoEventTracer,
    central_node_mid: CentralNodeWrapperMid,
):
    event_tracer.subscribe_event(
        central_node_mid.central_node, "telescopeState"
    )
    event_tracer.subscribe_event(central_node_mid.subarray_node, "obsState")

    central_node_mid.move_to_on()
    log_events(
        {
            central_node_mid.central_node: ["telescopeState"],
            central_node_mid.subarray_node: ["obsState"],
        }
    )
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        "'the TMC is On'"
        "TMC Central Node device"
        f"({central_node_mid.subarray_node.dev_name()}) "
        "is expected to be in ON telescope state",
    ).within_timeout(100).has_change_event_occurred(
        central_node_mid.central_node,
        "telescopeState",
        DevState.ON,
    )
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        "'the TMC is On'"
        "TMC Subarray device"
        f"({central_node_mid.subarray_node.dev_name()}) "
        "is expected to be in EMPTY obstate",
    ).within_timeout(100).has_change_event_occurred(
        central_node_mid.subarray_node,
        "obsState",
        ObsState.EMPTY,
    )
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "command_AssignResources", command_input_factory
    )

    # Invoke AssignResources() Command on TMC
    LOGGER.info("Invoking AssignResources command on TMC CentralNode")
    _, unique_id = central_node_mid.store_resources(assign_input_json)
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        "'the subarray must be in the IDLE obsState'"
        "TMC Subarray device"
        f"({central_node_mid.subarray_node.dev_name()}) "
        "is expected to be in IDLE obstate",
    ).within_timeout(60).has_change_event_occurred(
        central_node_mid.subarray_node,
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
        (unique_id[0], COMMAND_COMPLETED),
    )
    event_tracer.clear_events()


@when(
    parsers.parse(
        "I issue the command Configure passing an invalid JSON script to the subarray {subarray_id}"  # noqa: E501
    )
)
def invoke_configure_one(
    command_input_factory: JsonFactory,
    event_tracer: TangoEventTracer,
    subarray_node: SubarrayNodeWrapper,
):
    configure_input_json = prepare_json_args_for_commands(
        "command_Configure", command_input_factory
    )
    configure_json = json.loads(configure_input_json)
    del configure_json["csp"]["cbf"]["fsp"][0]["integration_factor"]
    pytest.command_result = subarray_node.execute_transition(
        "Configure", json.dumps(configure_input_json)
    )


@then(parsers.parse("the subarray {subarray_id} returns an error message"))
def invalid_command_rejection():
    # asserting error message and result code received from subarray
    assert "Malformed input string" in pytest.command_result[1][0]
    assert pytest.command_result[0][0] == ResultCode.REJECTED


@then(parsers.parse("the subarray {subarray_id} remains in obsState IDLE"))
def tmc_status(
    event_tracer: TangoEventTracer,
    central_node_mid: CentralNodeWrapperMid,
):
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        "'the subarray must be in the IDLE obsState'"
        "TMC Subarray device"
        f"({central_node_mid.subarray_node.dev_name()}) "
        "is expected to be in IDLE obstate",
    ).within_timeout(60).has_change_event_occurred(
        central_node_mid.subarray_node,
        "obsState",
        ObsState.IDLE,
    )


@when("I issue the command Configure passing a correct JSON script")
def tmc_accepts_command_with_valid_json(
    command_input_factory: JsonFactory,
    event_tracer: TangoEventTracer,
    subarray_node: SubarrayNodeWrapper,
):
    configure_input_json = prepare_json_args_for_commands(
        "command_Configure", command_input_factory
    )
    configure_input_json = json.loads(configure_input_json)
    configure_input_json["tmc"]["scan_duration"] = 10.0

    _, unique_id = subarray_node.execute_transition(
        "Configure", json.dumps(configure_input_json)
    )
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "WHEN" STEP: '
        "TMC Subarray Node device"
        f"({subarray_node.subarray_node.dev_name()}) "
        "is expected have longRunningCommand as"
        '(unique_id,(ResultCode.OK,"Command Completed"))',
    ).within_timeout(60).has_change_event_occurred(
        subarray_node.subarray_node,
        "longRunningCommandResult",
        (unique_id[0], COMMAND_COMPLETED),
    )


@then("the subarray transitions to obsState READY")
def tmc_status_ready(
    event_tracer: TangoEventTracer,
    subarray_node: SubarrayNodeWrapper,
):
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        "'the subarray must be in the READY obsState'"
        "TMC Subarray device"
        f"({subarray_node.subarray_node.dev_name()}) "
        "is expected to be in READY obstate",
    ).within_timeout(60).has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.READY,
    )
    event_tracer.clear_events()


@when("I issue the command Scan")
def tmc_accepts_scan_command(
    command_input_factory: JsonFactory,
    event_tracer: TangoEventTracer,
    subarray_node: SubarrayNodeWrapper,
):
    scan_input_json = prepare_json_args_for_commands(
        "command_Scan", command_input_factory
    )
    subarray_node.store_scan_data(scan_input_json)


@then("the subarray transitions to obsState SCANNING")
def tmc_status_scanning(event_tracer, subarray_node):
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "THEN" STEP: '
        "'the subarray transitions to obsState SCANNING'"
        "TMC Subarray device"
        f"({subarray_node.subarray_node.dev_name()}) "
        "is expected to be in SCANNING obstate",
    ).within_timeout(60).has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.SCANNING,
    )
    event_tracer.clear_events()


@when("I issue the command EndScan")
def tmc_accepts_endscan_command(
    event_tracer: TangoEventTracer,
    subarray_node: SubarrayNodeWrapper,
):
    subarray_node.remove_scan_data()


@then("implements the teardown")
def teardown_the_tmc(
    central_node_mid: CentralNodeWrapperMid,
    subarray_node: SubarrayNodeWrapper,
):
    """Tears down the system after test run"""
    subarray_node.tear_down()
    central_node_mid.tear_down()


@scenario(
    "../features/successful_scan_after_failed_configure.feature",
    "Invoke Configure command by passing a JSON script that uses resources which are not assigned to the subarray",  # noqa: E501
)
def test_configure_resource_with_unassigned_resources():
    """
    Test Configure command with input as json
    with resources that are not assigned.

    """


@when(
    parsers.parse(
        "I issue the command Configure passing an JSON script that uses resources which are not assigned to the subarray"  # noqa: E501
    )
)
def invoke_configure_with_unassigned_resources(
    command_input_factory: JsonFactory,
    subarray_node: SubarrayNodeWrapper,
):
    configure_input_json = prepare_json_args_for_commands(
        "command_Configure", command_input_factory
    )
    configure_input_json = json.loads(configure_input_json)
    configure_input_json["dish"]["receiver_band"] = "9"

    pytest.command_result = subarray_node.execute_transition(
        "Configure", json.dumps(configure_input_json)
    )


@then(parsers.parse("the subarray {subarray_id} returns an error message 2"))
def invalid_command_rejection_with_unassigned_resources():
    # asserting error message and result code received from subarray
    assert (
        "Malformed input string. Please check the JSON format."  # noqa: E501
        in pytest.command_result[1][0]
    )
    assert pytest.command_result[0][0] == ResultCode.REJECTED
