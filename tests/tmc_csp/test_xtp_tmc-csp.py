"""Test TMC-CSP Long Sequence of configure-scan functionality"""

import json
import logging

import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_ser_logging import configure_logging

from tests.resources.test_harness.helpers import (
    check_subarray_instance,
    prepare_json_args_for_commands,
    update_scan_id,
    update_scan_type,
)
from tests.resources.test_harness.utils.common_utils import (
    check_configure_successful,
    check_obsstate_csp_in_first_configure,
    check_scan_successful,
)

configure_logging(logging.DEBUG)
LOGGER = logging.getLogger(__name__)


@pytest.mark.tmc_csp
@scenario(
    "../features/tmc_csp/xtp_long_sequence_configure_scan.feature",
    "TMC Mid executes configure-scan sequence of commands successfully",
)
def test_tmc_csp_long_sequences():
    """
    Test case to verify TMC-CSP functionality with long sequences of commands
    """


@given("Telescope is ON state")
def given_a_tmc(central_node_mid, event_recorder, subarray_node):
    """A method to define TMC and CSP and subscribe ."""
    assert central_node_mid.central_node.ping() > 0
    assert central_node_mid.subarray_devices["csp_subarray"].ping() > 0
    event_recorder.subscribe_event(
        central_node_mid.central_node, "telescopeState"
    )
    event_recorder.subscribe_event(
        subarray_node.subarray_devices.get("csp_subarray"), "obsState"
    )

    event_recorder.subscribe_event(
        subarray_node.subarray_devices.get("csp_subarray"), "obsState"
    )
    event_recorder.subscribe_event(subarray_node.subarray_node, "obsState")
    event_recorder.subscribe_event(
        subarray_node.subarray_devices["csp_subarray"], "scanID"
    )
    event_recorder.subscribe_event(
        subarray_node.subarray_devices["csp_subarray"], "scanType"
    )

    event_recorder.subscribe_event(
        subarray_node.subarray_node, "longRunningCommandResult"
    )

    event_recorder.subscribe_event(
        central_node_mid.central_node, "longRunningCommandResult"
    )

    central_node_mid.move_to_on()

    assert event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "telescopeState",
        DevState.ON,
    )


@when(parsers.parse("I assign resources to TMC SubarrayNode {subarray_id}"))
def telescope_is_in_idle_state(
    central_node_mid,
    event_recorder,
    command_input_factory,
    subarray_id,
    subarray_node,
):
    """A method to move subarray into the IDLE ObsState."""

    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_mid_multiple_scantype", command_input_factory
    )

    assign_str = json.loads(assign_input_json)
    # Here we are adding this to get an event of ObsState CONFIGURING from
    # SDP Subarray
    assign_str["csp"]["processing_blocks"][0]["parameters"][
        "time-to-ready"
    ] = 2

    _, unique_id = central_node_mid.store_resources(json.dumps(assign_str))

    check_subarray_instance(
        subarray_node.subarray_devices.get("csp_subarray"), subarray_id
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_devices.get("csp_subarray"),
        "obsState",
        ObsState.IDLE,
    )

    check_subarray_instance(subarray_node.subarray_node, subarray_id)
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.IDLE,
    )

    assert event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "longRunningCommandResult",
        (unique_id[0], str(int(ResultCode.OK))),
        lookahead=5,
    )


@when(
    parsers.parse(
        "configure and scan TMC SubarrayNode {subarray_id} "
        "for each {scan_types} and {scan_ids}"
    )
)
def execute_configure_scan_sequence(
    subarray_node,
    command_input_factory,
    scan_ids,
    event_recorder,
    subarray_id,
    scan_types,
):
    """ "A method to invoke configure and scan  command"""

    check_subarray_instance(subarray_node.subarray_node, subarray_id)
    configure_json = prepare_json_args_for_commands(
        "configure1_mid", command_input_factory
    )

    configure_cycle = "initial"
    processed_scan_type = ""

    combined_dict = dict(zip(eval(scan_ids), eval(scan_types)))

    for scan_id, scan_type in combined_dict.items():
        configure_json = update_scan_type(configure_json, scan_type)
        _, unique_id = subarray_node.store_configuration_data(configure_json)
        if configure_cycle == "initial":
            check_obsstate_csp_in_first_configure(
                event_recorder, subarray_node
            )
            configure_cycle = "Next"

        check_configure_successful(
            subarray_node,
            event_recorder,
            unique_id,
            scan_type,
            processed_scan_type,
        )

        scan_json = prepare_json_args_for_commands(
            "scan_mid", command_input_factory
        )

        scan_json = update_scan_id(scan_json, scan_id)

        _, unique_id = subarray_node.execute_transition(
            "Scan", argin=scan_json
        )

        check_scan_successful(
            subarray_node, event_recorder, scan_id, unique_id
        )

        processed_scan_type = scan_type

        LOGGER.debug(
            f"Configure-scan sequence completed for {scan_id} "
            f"and scan_type {scan_type}"
        )

    # resources - TODO Validation to be added

    # event_recorder.subscribe_event(
    #     subarray_node.subarray_devices["sdp_subarray"], "resources"
    # )
    #
    # assert event_recorder.has_change_event_occurred(
    #     subarray_node.subarray_devices["sdp_subarray"],
    #     "resources",
    #     "csp_links",
    # )
