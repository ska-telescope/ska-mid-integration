"""Test TMC-SDP Long Sequence of configure-scan functionality"""

import logging

import pytest
from pytest_bdd import parsers, scenario, then, when
from ska_control_model import ObsState
from ska_ser_logging import configure_logging

from tests.resources.test_harness.helpers import (
    check_device_status_ready,
    check_device_status_scanning,
    check_subarray_instance,
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
    update_scan_id,
    update_scan_type,
)
from tests.resources.test_support.common_utils.common_helpers import Waiter
from tests.resources.test_support.common_utils.result_code import ResultCode

configure_logging(logging.DEBUG)
LOGGER = logging.getLogger(__name__)


def check_obsstate_sdp_in_first_configure(
    event_recorder, subarray_node
) -> None:
    """
    SDP doed not go to CONFIGURING in each CONFIGURE command
    except very first CONFIGURE command after Assign .
    Hence these checks are performed .
    """
    # TODO - Once SKB-309 is resolved , we can check and remove
    # this logic of configure_cycle
    # Currently SDP goes in configuring only in first configure
    # Command.
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_devices["sdp_subarray"],
        "obsState",
        ObsState.CONFIGURING,
    )
    check_device_status_ready(subarray_node.subarray_devices["sdp_subarray"])

    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_devices["sdp_subarray"],
        "obsState",
        ObsState.READY,
    )


def check_configure_successful(
    subarray_node, event_recorder, unique_id, scan_type, processed_scan_type
) -> None:
    """
    Adds check to verify if command is successful
    """
    check_device_status_ready(subarray_node.subarray_devices["sdp_subarray"])

    check_device_status_ready(subarray_node.subarray_node)
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.READY,
    )

    # Faced failure since scan type is set after SDP moves to READY
    # And some time that event is delayed.
    #  |1             |["1","2"]      |["science_A" , "science_A"] |
    # For same configuration scantype no event is pushed
    # https://gitlab.com/ska-telescope/sdp/ska-sdp-lmc/-/blob/master/src/ska_sdp_lmc/subarray/device.py#L548

    if scan_type != processed_scan_type:
        assert event_recorder.has_change_event_occurred(
            subarray_node.subarray_devices["sdp_subarray"],
            "scanType",
            scan_type,
        )

    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "longRunningCommandResult",
        (unique_id[0], str(int(ResultCode.OK))),
        lookahead=5,
    )


@pytest.mark.tmc_sdp
@scenario(
    "../features/tmc_sdp/xtp-35244_long_sequence_configure_scan.feature",
    "TMC executes configure-scan sequence of commands successfully",
)
def test_tmc_sdp_long_sequences():
    """
    Test case to verify TMC-SDP  functionality with long sequences of commands
    """


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
        "sdp_mid_configure1", command_input_factory
    )

    configure_cycle = "initial"
    processed_scan_type = "None"

    combined_dict = dict(zip(eval(scan_ids), eval(scan_types)))
    LOGGER.debug(f"combined_dict {combined_dict}")

    for scan_id, scan_type in combined_dict.items():

        configure_json = update_scan_type(configure_json, scan_type)
        _, unique_id = subarray_node.store_configuration_data(configure_json)
        if configure_cycle == "initial":
            check_obsstate_sdp_in_first_configure(
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

        LOGGER.info(f"updated scan {scan_json}")
        _, unique_id = subarray_node.execute_transition(
            "Scan", argin=scan_json
        )

        # Faced a delay while testing , hence adding waiter here.

        check_device_status_scanning(subarray_node.subarray_node)

        assert event_recorder.has_change_event_occurred(
            subarray_node.subarray_node,
            "obsState",
            ObsState.SCANNING,
        )
        assert event_recorder.has_change_event_occurred(
            subarray_node.subarray_devices["sdp_subarray"],
            "obsState",
            ObsState.SCANNING,
        )
        assert event_recorder.has_change_event_occurred(
            subarray_node.subarray_devices["sdp_subarray"],
            "scanID",
            int(scan_id),
        )

        # The sdp subarray transitions to READY after the scan duration
        # elapsed

        check_device_status_ready(
            subarray_node.subarray_devices["sdp_subarray"]
        )
        assert event_recorder.has_change_event_occurred(
            subarray_node.subarray_devices["sdp_subarray"],
            "obsState",
            ObsState.READY,
        )

        check_device_status_ready(subarray_node.subarray_node)
        assert event_recorder.has_change_event_occurred(
            subarray_node.subarray_node,
            "obsState",
            ObsState.READY,
        )
        assert event_recorder.has_change_event_occurred(
            subarray_node.subarray_node,
            "longRunningCommandResult",
            (unique_id[0], str(int(ResultCode.OK))),
            lookahead=5,
        )

        processed_scan_type = scan_type

        LOGGER.info("Configure-scan round completed   ")

    LOGGER.info("Configure Scan Completed")

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


@when(parsers.parse("end the configuration on TMC SubarrayNode {subarray_id}"))
def execute_end_command(
    subarray_node,
    command_input_factory,
    central_node_mid,
    event_recorder,
    subarray_id,
    scan_types,
):
    """ "A method to invoke end command"""

    central_node_mid.set_subarray_id(subarray_id)
    subarray_node.execute_transition("End")
    the_waiter = Waiter()
    the_waiter.set_wait_for_specific_obsstate(
        "IDLE", [subarray_node.subarray_node]
    )
    the_waiter.wait(100)

    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_devices["sdp_subarray"],
        "obsState",
        ObsState.IDLE,
    )


@when(parsers.parse("release the resources on TMC SubarrayNode {subarray_id}"))
def execute_release_resources_command(
    command_input_factory,
    central_node_mid,
    event_recorder,
    subarray_id,
):
    """ "A method to invoke Release Resources command"""

    release_input_json = prepare_json_args_for_centralnode_commands(
        "release_resources_mid", command_input_factory
    )
    check_subarray_instance(central_node_mid.subarray_node, subarray_id)
    central_node_mid.invoke_release_resources(release_input_json)

    """Method to check SDP is in EMPTY obsstate"""
    check_subarray_instance(
        central_node_mid.subarray_devices.get("sdp_subarray"), subarray_id
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.subarray_devices.get("sdp_subarray"),
        "obsState",
        ObsState.EMPTY,
    )


@then(
    parsers.parse(
        "TMC SubarrayNode {subarray_id} transitions to EMPTY ObsState"
    )
)
def check_tmc_is_in_empty_obsstate(
    central_node_mid, event_recorder, subarray_id
):
    """Method to check TMC is in EMPTY obsstate."""
    check_subarray_instance(central_node_mid.subarray_node, subarray_id)
    assert event_recorder.has_change_event_occurred(
        central_node_mid.subarray_node,
        "obsState",
        ObsState.EMPTY,
    )
