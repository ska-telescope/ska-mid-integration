"""Test module for check unavailability of dish functionality"""


import os
import time

import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_tango_base.control_model import ObsState
from tango import DeviceProxy, DevState
from tango.db import Database

from tests.resources.test_harness.central_node_mid import CentralNodeWrapperMid
from tests.resources.test_harness.event_recorder import EventRecorder
from tests.resources.test_harness.helpers import (
    check_for_device_command_event,
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
)
from tests.resources.test_harness.subarray_node import SubarrayNodeWrapper

# from tests.resources.test_harness.tmc_mid import TMCMid
from tests.resources.test_harness.utils.common_utils import JsonFactory
from tests.resources.test_support.common_utils.common_helpers import Resource
from tests.resources.test_support.common_utils.result_code import ResultCode
from tests.resources.test_support.enum import DishMode

# from tango import DevState


@pytest.mark.skip
@pytest.mark.tmc_dish
@scenario(
    "../features/tmc_dish/xtp-nnnn_unavailability_dish.feature",
    "Dish manager reports the error when one of the subsystem is unavailable",
)
def test_tmc_dish_unavailability_functionality():
    """
    Test case to verify TMC-DISH dish unavailability functionality
    """


@given("a telescope in OFF or STANDBY state")
def check_telescope_in_initial_state(
    central_node_mid: CentralNodeWrapperMid, event_recorder: EventRecorder
):
    """
    Given a TMC
    """
    event_recorder.subscribe_event(
        central_node_mid.central_node, "telescopeState"
    )

    Resource(central_node_mid.central_node).assert_attribute(
        "telescopeState"
    ).equals(["OFF", "STANDBY"])


@given("the TMC subarray is in IDLE obsState")
def move_subarray_to_obsState_idle(
    subarray_node: SubarrayNodeWrapper,
    central_node_mid: CentralNodeWrapperMid,
    event_recorder: EventRecorder,
    command_input_factory: JsonFactory,
):
    """
    Method to move subarray in IDLE obsState
    """
    central_node_mid.move_to_on()
    event_recorder.subscribe_event(central_node_mid.csp_master, "State")
    event_recorder.subscribe_event(central_node_mid.sdp_master, "State")

    assert event_recorder.has_change_event_occurred(
        central_node_mid.csp_master,
        "State",
        DevState.ON,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.sdp_master,
        "State",
        DevState.ON,
    )

    for dish_id in ["SKA001", "SKA036", "SKA063", "SKA100"]:
        event_recorder.subscribe_event(
            central_node_mid.dish_master_dict[dish_id], "dishMode"
        )
        event_recorder.subscribe_event(
            central_node_mid.dish_leaf_node_dict[dish_id], "dishMode"
        )

        assert event_recorder.has_change_event_occurred(
            central_node_mid.dish_master_dict[dish_id],
            "dishMode",
            DishMode.STANDBY_FP,
        )
        assert event_recorder.has_change_event_occurred(
            central_node_mid.dish_leaf_node_dict[dish_id],
            "dishMode",
            DishMode.STANDBY_FP,
        )

    event_recorder.subscribe_event(
        central_node_mid.central_node, "telescopeState"
    )

    assert event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "telescopeState",
        DevState.ON,
    )

    event_recorder.subscribe_event(subarray_node.subarray_node, "obsState")

    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_mid", command_input_factory
    )
    pytest.command_result = central_node_mid.store_resources(assign_input_json)

    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.IDLE,
    )
    event_recorder.subscribe_event(
        central_node_mid.central_node, "longRunningCommandResult"
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "longRunningCommandResult",
        (pytest.command_result[1][0], str(ResultCode.OK.value)),
    )


@when("one of the dish subsystems CommunicationStatus is made NOT_ESTABLISHED")
def restart_the_dish_leaf_nodes():
    """Restart the dish leaf nodes"""
    # tmc_mid.RestartServer("SPFRX")
    dish_name_1 = os.getenv("DISH_NAMESPACE_1")
    spfrx_fqdn = (
        f"tango://tango-databaseds.{dish_name_1}.svc.cluster"
        ".local:10000/mid-dish/simulator-spfrx/SKA001"
    )
    spfrx_deviceproxy = DeviceProxy(spfrx_fqdn)
    spfrx_tango_host = spfrx_fqdn.split("/")[2]
    spfrx_host = spfrx_tango_host.split(":")[0]
    spfrx_port = spfrx_tango_host.split(":")[1]
    spfrx_db = Database(spfrx_host, spfrx_port)
    spfrx_db.delete_device(spfrx_fqdn)
    spfrx_admin_dev_name = spfrx_deviceproxy.adm_name()
    spfrx_admin_dev_proxy = DeviceProxy(spfrx_admin_dev_name)
    spfrx_admin_dev_proxy.RestartServer()
    time.sleep(3)


@when(parsers.parse("I configure the subarray {subarray_id}"))
def configure_subarray(
    subarray_node: SubarrayNodeWrapper,
    central_node_mid: CentralNodeWrapperMid,
    event_recorder: EventRecorder,
    command_input_factory: JsonFactory,
    subarray_id: str,
):
    """
    A method to invoke first Configure command
    """
    event_recorder.subscribe_event(
        subarray_node.subarray_node, "longRunningCommandResult"
    )

    configure_input_json = prepare_json_args_for_commands(
        "configure_mid", command_input_factory
    )
    central_node_mid.set_subarray_id(subarray_id)
    pytest.command_result = subarray_node.execute_transition(
        "Configure", configure_input_json
    )


@then("dish manager should throw the error and report to TMC")
def dish_lmc_reprorts_unavailibiltiy(event_recorder, central_node_mid):
    exception_message = (
        "The processing controller, helm deployer, or both "
        + "are OFFLINE: cannot start processing blocks."
    )
    for dish_id in ["SKA001", "SKA036", "SKA063", "SKA100"]:
        event_recorder.subscribe_event(
            central_node_mid.dish_master_dict[dish_id],
            "longRunningCommandStatus",
        )
        assert check_for_device_command_event(
            central_node_mid.dish_master_dict[dish_id],
            "longRunningCommandStatus",
            exception_message,
            event_recorder,
            "Configure",
        )


@then("TMC should propagate the error to client")
def tmc_reports_unavailability_to_client(
    event_recorder: EventRecorder, central_node_mid: CentralNodeWrapperMid
):
    """
    Method to verify TMC subarray reports unavailability to client.
    """
    pass
    # exception_message = (
    #     "Exception occurred on device:"
    #     + " ska_mid/tm_subarray_node/1: Exception occurred on the"
    #     + " following devices: ska_mid/tm_leaf_node/sdp_subarray01:"
    #     + " The processing controller, helm deployer, or both are OFFLINE:"
    #     + " cannot start processing blocks.\n"
    # )
    # event_recorder.subscribe_event(
    #     central_node_mid.central_node,
    #     "longRunningCommandResult",
    # )
    # assert check_for_device_command_event(
    #     central_node_mid.central_node,
    #     "longRunningCommandResult",
    #     exception_message,
    #     event_recorder,
    #     "AssignResources",
    # )


@then(
    parsers.parse(
        "the TMC SubarrayNode {subarray_id} remains in ObsState CONFIGURING"
    )
)
def subarray_is_in_configuring_obsState(
    subarray_node,
    event_recorder,
    subarray_id,
):
    """
    A method to check if telescope in is configuring obsState
    """
    subarray_node.set_subarray_id(subarray_id)
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.CONFIGURING,
        lookahead=10,
    )
