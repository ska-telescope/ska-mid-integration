"""Test module for check unavailability of dish functionality"""


import logging
import os
import time

import pytest
from pytest_bdd import given, scenario, when
from ska_tango_base.control_model import ObsState
<<<<<<< HEAD
from tango import DeviceProxy
from tango.db import Database
=======
from tango import DevState
>>>>>>> 3b52eb24 (SAH-1536: Add test case for tmc-dish unavailability)

from tests.resources.test_harness.central_node_mid import CentralNodeWrapperMid
from tests.resources.test_harness.event_recorder import EventRecorder
from tests.resources.test_harness.helpers import (
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
)
from tests.resources.test_harness.subarray_node import SubarrayNodeWrapper
from tests.resources.test_harness.utils.common_utils import JsonFactory
from tests.resources.test_support.common_utils.result_code import ResultCode
from tests.resources.test_support.enum import DishMode

LOGGER = logging.getLogger(__name__)


@pytest.mark.tmc_dish
@scenario(
    "../features/tmc_dish/xtp-nnnn_unavailability_dish.feature",
    "Dish manager reports the error when one of the subsystem is unavailable",
)
def test_tmc_dish_unavailability_functionality():
    """
    Test case to verify TMC-DISH dish unavailability functionality
    """


spfrx_dev_name = os.getenv("SPFRX_NAME_1")
dish_name1 = os.getenv("DISH_NAME_1")


@given(
    parsers.parse(
        "a Telescope consisting of TMC, DISH {dish_ids},"
        + " simulated CSP and simulated SDP"
    )
)
def given_a_telescope(central_node_mid, dish_ids):
    """
    Given a TMC
    """
<<<<<<< HEAD
    event_recorder.subscribe_event(
        central_node_mid.central_node, "telescopeState"
    )
    for dish_id in ["SKA001", "SKA036", "SKA063", "SKA100"]:
        event_recorder.subscribe_event(
            central_node_mid.dish_master_dict[dish_id], "dishMode"
        )

        assert event_recorder.has_change_event_occurred(
            central_node_mid.dish_master_dict[dish_id],
            "dishMode",
            DishMode.STANDBY_LP,
        )
    # Wait for DishMaster attribute value update,
    # on CentralNode for value dishMode STANDBY_LP

    # TODO: Improvement in tests/implementation
    # to minimize the need of having sleep
    time.sleep(5)
    Resource(central_node_mid.central_node).assert_attribute(
        "telescopeState"
    ).equals(["OFF", "STANDBY"])
=======
    assert central_node_mid.csp_master.ping() > 0
    assert central_node_mid.sdp_master.ping() > 0
    for dish_id in dish_ids.split(","):
        assert central_node_mid.dish_master_dict[dish_id].ping() > 0
        assert central_node_mid.dish_leaf_node_dict[dish_id].ping() > 0
>>>>>>> 3b52eb24 (SAH-1536: Add test case for tmc-dish unavailability)


@given("the Telescope is in ON state")
def turn_on_telescope(central_node_mid, event_recorder):
    """
    A method to put Telescope ON
    """
    event_recorder.subscribe_event(subarray_node.subarray_node, "obsState")
    event_recorder.subscribe_event(
        central_node_mid.central_node, "longRunningCommandResult"
    )
    central_node_mid.move_to_on()
    for dish_id in ["SKA001", "SKA036", "SKA063", "SKA100"]:
        event_recorder.subscribe_event(
            central_node_mid.dish_master_dict[dish_id], "dishMode"
        )

        assert event_recorder.has_change_event_occurred(
            central_node_mid.dish_master_dict[dish_id],
            "dishMode",
            DishMode.STANDBY_FP,
        )
<<<<<<< HEAD
=======
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


@given("TMC subarray is in IDLE obsState")
def check_subarray_obsState_idle(
    subarray_node, central_node_mid, event_recorder, command_input_factory
):
    """
    Method to check subarray is in IDLE obsState
    """
    event_recorder.subscribe_event(subarray_node.subarray_node, "obsState")
>>>>>>> 3b52eb24 (SAH-1536: Add test case for tmc-dish unavailability)

    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_mid", command_input_factory
    )
    pytest.command_result = central_node_mid.store_resources(assign_input_json)

    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.IDLE,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "longRunningCommandResult",
        (pytest.command_result[1][0], str(ResultCode.OK.value)),
    )


@when("one of the dish subsystems CommunicationStatus is made NOT_ESTABLISHED")
def restart_the_dish_leaf_nodes(central_node_mid):
    """Restart the dish leaf nodes"""

    LOGGER.info("dish1 device name is: %s", dish_name1)
    LOGGER.info("spfrx device name is : %s", spfrx_dev_name)
    # check_spfrx_info = central_node_mid.dish1_db.get_device_info(
    #     "mid-dish/simulator-spfrx/SKA001"
    # )
    # LOGGER.info("spfrx device info is: %s", check_spfrx_info)
    # spfrx_exported = central_node_mid.dish1_db.get_device_exported(
    #     "mid-dish/simulator-spfrx/SKA001"
    # )
    # LOGGER.info("spfrx device exported : %s", spfrx_exported)
    # import tango
    # spfrx_proxy = tango.DeviceProxy(spfrx_exported)
    # LOGGER.info("spfrx device proxy : %s", spfrx_proxy)
    # central_node_mid.dish1_db.delete_device(spfrx_proxy)
    spfrx_fqdn = (
        "tango://tango-databaseds.dish-lmc-1.svc.cluster.local:10000/"
        "mid-dish/simulator-spfrx/SKA001"
    )
    central_node_mid.dish1_db.delete_device(spfrx_fqdn)
    LOGGER.info("spfrx deleted")
    central_node_mid.dish1_admin_dev_proxy.RestartServer()
    # Added a wait for the completion of dish device deletion from TANGO
    # database and the dish device restart
    time.sleep(5)


@when("I configure the subarray {subarray_id}")
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
<<<<<<< HEAD
    pytest.command_result = subarray_node.store_configuration_data(
        configure_input_json
    )
=======
    pytest.command_result = subarray_node.execute_transition(
        "Configure", configure_input_json
    )


@then("dish manager should throw the error and report to TMC")
def dish_lmc_reprorts_unavailibiltiy(event_recorder, central_node_mid):
    pass
    # exception_message = (
    #     "The processing controller, helm deployer, or both "
    #     + "are OFFLINE: cannot start processing blocks."
    # )
    # for dish_id in ["SKA001", "SKA036", "SKA063", "SKA100"]:
    #     event_recorder.subscribe_event(
    #         central_node_mid.dish_master_dict[dish_id],
    #         "longRunningCommandStatus",
    #     )
    #     assert check_for_device_command_event(
    #         central_node_mid.dish_master_dict[dish_id],
    #         "longRunningCommandStatus",
    #         exception_message,
    #         event_recorder,
    #         "Configure",
    #     )


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
    # subarray_node.set_subarray_id(subarray_id)
    # assert event_recorder.has_change_event_occurred(
    #     subarray_node.subarray_node,
    #     "obsState",
    #     ObsState.CONFIGURING,
    #     lookahead=10,
    # )
    pass
>>>>>>> 3b52eb24 (SAH-1536: Add test case for tmc-dish unavailability)
