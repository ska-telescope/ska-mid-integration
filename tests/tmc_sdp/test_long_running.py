"""Test TMC-SDP Long Sequence  functionality"""

import json
import logging

import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState
from ska_ser_logging import configure_logging
from tango import DevState

from tests.resources.test_harness.helpers import (
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


@pytest.mark.trupti
@pytest.mark.tmc_sdp
@scenario(
    "../features/tmc_sdp/long_running.feature",
    "TMC executes long sequence of commands successfully",
)
def test_tmc_sdp_long_sequences():
    """
    Test case to verify TMC-SDP  functionality with long sequences of commands
    """


def check_device_status_ready(device_name):
    """
    Checks if given device is in READY obs-state
    """
    the_waiter = Waiter()
    the_waiter.set_wait_for_specific_obsstate("READY", [device_name])
    the_waiter.wait(100)


def check_device_status_scanning(device_name):
    """
    Checks if given device is in READY obs-state
    """
    the_waiter = Waiter()
    the_waiter.set_wait_for_specific_obsstate("READY", [device_name])
    the_waiter.wait(200)


@given("Telescope is ON state")
def given_a_tmc(central_node_mid, event_recorder, subarray_node):
    """A method to define TMC and SDP and subscribe ."""
    assert central_node_mid.central_node.ping() > 0
    assert central_node_mid.subarray_devices["sdp_subarray"].ping() > 0
    event_recorder.subscribe_event(
        central_node_mid.central_node, "telescopeState"
    )
    event_recorder.subscribe_event(
        subarray_node.subarray_devices.get("sdp_subarray"), "obsState"
    )

    event_recorder.subscribe_event(
        subarray_node.subarray_devices.get("csp_subarray"), "obsState"
    )
    event_recorder.subscribe_event(subarray_node.subarray_node, "obsState")
    event_recorder.subscribe_event(
        subarray_node.subarray_devices["sdp_subarray"], "scanID"
    )
    event_recorder.subscribe_event(
        subarray_node.subarray_devices["sdp_subarray"], "scanType"
    )

    event_recorder.subscribe_event(
        subarray_node.subarray_node, "longRunningCommandResult"
    )
    central_node_mid.move_to_on()

    assert event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "telescopeState",
        DevState.ON,
    )
    LOGGER.info("On step completed")


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
    # Here we are adding this to get an event of ObsState CONFIGURING from SDP
    # Subarray
    assign_str["sdp"]["processing_blocks"][0]["parameters"][
        "time-to-ready"
    ] = 2

    central_node_mid.store_resources(json.dumps(assign_str))

    check_subarray_instance(
        subarray_node.subarray_devices.get("sdp_subarray"), subarray_id
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_devices.get("sdp_subarray"),
        "obsState",
        ObsState.IDLE,
    )

    check_subarray_instance(subarray_node.subarray_node, subarray_id)
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.IDLE,
    )
    LOGGER.info("Assign resources  completed")


@when(
    parsers.parse(
        "configure and scan TMC SubarrayNode {subarray_id} "
        "for each {scan_types} and {scan_ids}"
    )
)
def execute_initial_configure_command(
    subarray_node,
    command_input_factory,
    scan_ids,
    event_recorder,
    subarray_id,
    scan_types,
):
    """ "A method to invoke configure command"""

    check_subarray_instance(subarray_node.subarray_node, subarray_id)
    configure_json = prepare_json_args_for_commands(
        "sdp_mid_configure1", command_input_factory
    )

    my_list = eval(scan_types)
    LOGGER.info(f"working on scan types {my_list} ")

    scan_id_list = eval(scan_ids)

    LOGGER.info(f"working with scan ids {scan_ids}")
    LOGGER.info(f"scan_id_list {scan_id_list}")
    LOGGER.info(f"type {type(scan_id_list)}")
    configure_cycle = "initial"
    processed_scan_type = "None"

    for scan_id in scan_id_list:
        LOGGER.info(f" scan_id is {scan_id}")
        LOGGER.info(f"type is {type(scan_id)}")

        for scan_type in my_list:
            LOGGER.info(f" scan_type is {scan_type}")

            configure_json = update_scan_type(configure_json, scan_type)
            _, unique_id = subarray_node.store_configuration_data(
                configure_json
            )
            if configure_cycle == "initial":
                # TODO - Once SKB-309 is resolved , we can check and remove
                # this logic of configure_cycle
                # Currently SDP goes in configuring only in first configure
                # Command.
                assert event_recorder.has_change_event_occurred(
                    subarray_node.subarray_devices["sdp_subarray"],
                    "obsState",
                    ObsState.CONFIGURING,
                )
                check_device_status_ready(
                    subarray_node.subarray_devices["sdp_subarray"]
                )
                assert event_recorder.has_change_event_occurred(
                    subarray_node.subarray_devices["sdp_subarray"],
                    "obsState",
                    ObsState.READY,
                )

                configure_cycle = "Next"

            check_device_status_ready(
                subarray_node.subarray_devices["sdp_subarray"]
            )

            # READY Event will not come ,since SDP was already in Ready
            # assert event_recorder.has_change_event_occurred(
            #     subarray_node.subarray_devices["sdp_subarray"],
            #     "obsState",
            #     ObsState.READY,
            # )

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
            # Do we want to adjust test case to accommodate this ?
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

    # resources

    # event_recorder.subscribe_event(
    #     subarray_node.subarray_devices["sdp_subarray"], "resources"
    # )
    #
    # assert event_recorder.has_change_event_occurred(
    #     subarray_node.subarray_devices["sdp_subarray"],
    #     "resources",
    #     "csp_links",
    # )


# @when("the subarray transitions to obsState READY")
# def check_subarray_in_ready(subarray_node, event_recorder):
#     """A method to check SDP subarray obsstate"""
#
#     assert event_recorder.has_change_event_occurred(
#         subarray_node.subarray_devices["sdp_subarray"],
#         "obsState",
#         ObsState.READY,
#     )
#     assert event_recorder.has_change_event_occurred(
#         subarray_node.subarray_devices["csp_subarray"],
#         "obsState",
#         ObsState.READY,
#     )
#     assert event_recorder.has_change_event_occurred(
#         subarray_node.subarray_node,
#         "obsState",
#         ObsState.READY,
#     )
#
#
# @when(
#     parsers.parse(
#         "the next successive configure command is issued with {input_json2}"
#     )
# )
# def execute_next_configure_command(
#     subarray_node, command_input_factory, input_json2
# ):
#     """ "A method to invoke configure command"""
#
#     configure_json = prepare_json_args_for_commands(
#         input_json2, command_input_factory
#     )
#     subarray_node.store_configuration_data(configure_json)
#
#     # TODO :: Issue is raised with SDP team , awating for
#     #  confirmation to raise it as bug
#     # assert event_recorder.has_change_event_occurred(
#     #     subarray_node.subarray_devices["sdp_subarray"],
#     #     "obsState",
#     #     ObsState.CONFIGURING,
#     # )
#
#
# @then(
#     parsers.parse(
#         "the subarray {subarray_id} reconfigures changing its "
#         "obsState to READY"
#     )
# )
# def check_subarray_in_ready_in_reconfigure(
#     central_node_mid, subarray_node, event_recorder, subarray_id
# ):
#     """A method to check SDP subarray obsstate"""
#
#     # TODO :: Issue is raised with SDP team ,
#     #  awating for confirmation to raise it as bug
#     # check_subarray_instance(
#     #     central_node_mid.subarray_devices.get("sdp_subarray"), subarray_id
#     # )
#     #
#     # assert event_recorder.has_change_event_occurred(
#     #     subarray_node.subarray_devices["sdp_subarray"],
#     #     "obsState",
#     #     ObsState.READY,
#     # )
#
#     check_subarray_instance(central_node_mid.subarray_node, subarray_id)
#     assert event_recorder.has_change_event_occurred(
#         subarray_node.subarray_node,
#         "obsState",
#         ObsState.READY,
#     )


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
