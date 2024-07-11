"""Test module for check unavailability of dish functionality"""

<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD

import logging
import os
=======
>>>>>>> 05994d75 (SAH-1536: Implemented test case for unavailaity scenario)
import time
=======
>>>>>>> 0da5aa4b (SAH-1536: Updated test case)

import os
import time

import pytest
from pytest_bdd import given, scenario, when
from ska_tango_base.control_model import ObsState
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
from tango import DeviceProxy
from tango.db import Database
=======
from tango import DevState
>>>>>>> 3b52eb24 (SAH-1536: Add test case for tmc-dish unavailability)
=======
from tango import DevState
>>>>>>> 05994d75 (SAH-1536: Implemented test case for unavailaity scenario)
=======
>>>>>>> 1de465a4 (SAH-1536: Update test case)
=======
from tango import DeviceProxy
from tango.db import Database
>>>>>>> 8ee2d95e (SAH-1536: Update test case)
=======

import logging
import os
import time

import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_tango_base.control_model import ObsState
from tango import DevState
>>>>>>> 455c6266 (SAH-1536: Implement unhappy path tests for tmc-dish pair)

from tests.resources.test_harness.central_node_mid import CentralNodeWrapperMid
from tests.resources.test_harness.event_recorder import EventRecorder
from tests.resources.test_harness.helpers import (
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
)
from tests.resources.test_harness.subarray_node import SubarrayNodeWrapper
<<<<<<< HEAD

# from tests.resources.test_harness.tmc_mid import TMCMid
from tests.resources.test_harness.utils.common_utils import JsonFactory
from tests.resources.test_support.common_utils.common_helpers import Resource
from tests.resources.test_support.common_utils.result_code import ResultCode
from tests.resources.test_support.enum import DishMode

<<<<<<< HEAD
<<<<<<< HEAD
LOGGER = logging.getLogger(__name__)

=======
>>>>>>> 05994d75 (SAH-1536: Implemented test case for unavailaity scenario)
=======
# from tango import DevState

>>>>>>> 1de465a4 (SAH-1536: Update test case)

@pytest.mark.skip
=======
from tests.resources.test_harness.utils.common_utils import JsonFactory
from tests.resources.test_support.common_utils.result_code import ResultCode
from tests.resources.test_support.enum import DishMode

LOGGER = logging.getLogger(__name__)

spfrx_dev_name = os.getenv("SPFRX_NAME_1")


>>>>>>> 455c6266 (SAH-1536: Implement unhappy path tests for tmc-dish pair)
@pytest.mark.tmc_dish
@scenario(
    "../features/tmc_dish/xtp-nnnn_unavailability_dish.feature",
    "Dish manager reports the error when one of the subsystem is unavailable",
)
def test_tmc_dish_unavailability_functionality():
    """
    Test case to verify TMC-DISH dish unavailability functionality
    """


<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
spfrx_dev_name = os.getenv("SPFRX_NAME_1")
dish_name1 = os.getenv("DISH_NAME_1")


=======
>>>>>>> 455c6266 (SAH-1536: Implement unhappy path tests for tmc-dish pair)
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
<<<<<<< HEAD
    event_recorder.subscribe_event(
        central_node_mid.central_node, "telescopeState"
    )
=======
@given("a telescope in ON state")
def check_telescope_is_on(
    central_node_mid: CentralNodeWrapperMid, event_recorder: EventRecorder
):
    "check telescope is in On state"
<<<<<<< HEAD
<<<<<<< HEAD
>>>>>>> 05994d75 (SAH-1536: Implemented test case for unavailaity scenario)
=======
=======
    for dish_id in ["SKA001", "SKA036", "SKA063", "SKA100"]:
        assert central_node_mid.dish_master_dict[dish_id].ping() > 0
>>>>>>> 9a8a6eea (SAH-1536: Update test case)
=======
@given("a telescope in OFF or STANDBY state")
def check_telescope_in_initial_state(
    central_node_mid: CentralNodeWrapperMid, event_recorder: EventRecorder
):
    """
    Given a TMC
    """
>>>>>>> 1de465a4 (SAH-1536: Update test case)
    event_recorder.subscribe_event(
        central_node_mid.central_node, "telescopeState"
    )
>>>>>>> 406e959d (SAH-1536: Updated test case)
    for dish_id in ["SKA001", "SKA036", "SKA063", "SKA100"]:
        event_recorder.subscribe_event(
            central_node_mid.dish_master_dict[dish_id], "dishMode"
        )

        assert event_recorder.has_change_event_occurred(
            central_node_mid.dish_master_dict[dish_id],
            "dishMode",
            DishMode.STANDBY_LP,
        )
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
    # Wait for DishMaster attribute value update,
    # on CentralNode for value dishMode STANDBY_LP

<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
    # TODO: Improvement in tests/implementation
    # to minimize the need of having sleep
    time.sleep(5)
    Resource(central_node_mid.central_node).assert_attribute(
        "telescopeState"
    ).equals(["OFF", "STANDBY"])
=======
=======
>>>>>>> 455c6266 (SAH-1536: Implement unhappy path tests for tmc-dish pair)
    assert central_node_mid.csp_master.ping() > 0
    assert central_node_mid.sdp_master.ping() > 0
    for dish_id in dish_ids.split(","):
        assert central_node_mid.dish_master_dict[dish_id].ping() > 0
        assert central_node_mid.dish_leaf_node_dict[dish_id].ping() > 0
<<<<<<< HEAD
>>>>>>> 3b52eb24 (SAH-1536: Add test case for tmc-dish unavailability)
=======
>>>>>>> 455c6266 (SAH-1536: Implement unhappy path tests for tmc-dish pair)


@given("the Telescope is in ON state")
def turn_on_telescope(central_node_mid, event_recorder):
    """
    A method to put Telescope ON
    """
<<<<<<< HEAD
    event_recorder.subscribe_event(subarray_node.subarray_node, "obsState")
    event_recorder.subscribe_event(
        central_node_mid.central_node, "longRunningCommandResult"
    )
    central_node_mid.move_to_on()
=======
    if central_node_mid.telescope_state != "ON":
        central_node_mid.move_to_on()
=======
    central_node_mid.move_to_on()
>>>>>>> 9dd50191 (SAH-1536: Updated test case)

<<<<<<< HEAD
>>>>>>> 05994d75 (SAH-1536: Implemented test case for unavailaity scenario)
=======
    time.sleep(2)
>>>>>>> 927fa5a7 (SAH-1536: Updated test case)
=======
>>>>>>> 9a8a6eea (SAH-1536: Update test case)
=======
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

>>>>>>> 455c6266 (SAH-1536: Implement unhappy path tests for tmc-dish pair)
    for dish_id in ["SKA001", "SKA036", "SKA063", "SKA100"]:
        event_recorder.subscribe_event(
            central_node_mid.dish_master_dict[dish_id], "dishMode"
        )
<<<<<<< HEAD
=======
        event_recorder.subscribe_event(
            central_node_mid.dish_leaf_node_dict[dish_id], "dishMode"
        )
>>>>>>> 455c6266 (SAH-1536: Implement unhappy path tests for tmc-dish pair)

        assert event_recorder.has_change_event_occurred(
            central_node_mid.dish_master_dict[dish_id],
            "dishMode",
            DishMode.STANDBY_FP,
<<<<<<< HEAD
<<<<<<< HEAD
            lookahead=12,
        )
<<<<<<< HEAD
<<<<<<< HEAD
=======
=======
        )
>>>>>>> 455c6266 (SAH-1536: Implement unhappy path tests for tmc-dish pair)
        assert event_recorder.has_change_event_occurred(
            central_node_mid.dish_leaf_node_dict[dish_id],
            "dishMode",
            DishMode.STANDBY_FP,
        )

    event_recorder.subscribe_event(
        central_node_mid.central_node, "telescopeState"
    )

<<<<<<< HEAD
=======
=======
>>>>>>> 16a56ef7 (SAH-1536: Updated test case)
=======
    assert event_recorder.has_change_event_occurred(
        central_node_mid.dish_master_dict["SKA001"],
        "dishMode",
        DishMode.STANDBY_FP,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.dish_master_dict["SKA036"],
        "dishMode",
        DishMode.STANDBY_FP,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.dish_master_dict["SKA063"],
        "dishMode",
        DishMode.STANDBY_FP,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.dish_master_dict["SKA100"],
        "dishMode",
        DishMode.STANDBY_FP,
    )
=======
        )
>>>>>>> 9a8a6eea (SAH-1536: Update test case)

>>>>>>> 0af5cb2f (SAH-1536: Update test case)
=======
>>>>>>> 1de465a4 (SAH-1536: Update test case)
    # Wait for DishMaster attribute value update,
    # on CentralNode for value dishMode STANDBY_LP

    # TODO: Improvement in tests/implementation
    # to minimize the need of having sleep
    time.sleep(5)
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
>>>>>>> 05994d75 (SAH-1536: Implemented test case for unavailaity scenario)
=======
>>>>>>> 0da5aa4b (SAH-1536: Updated test case)
=======
>>>>>>> 16a56ef7 (SAH-1536: Updated test case)
=======

>>>>>>> 0af5cb2f (SAH-1536: Update test case)
=======
>>>>>>> 455c6266 (SAH-1536: Implement unhappy path tests for tmc-dish pair)
    assert event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "telescopeState",
        DevState.ON,
    )
<<<<<<< HEAD
=======
    Resource(central_node_mid.central_node).assert_attribute(
        "telescopeState"
    ).equals(["OFF", "STANDBY"])
>>>>>>> 1de465a4 (SAH-1536: Update test case)


<<<<<<< HEAD
=======


>>>>>>> 455c6266 (SAH-1536: Implement unhappy path tests for tmc-dish pair)
@given("TMC subarray is in IDLE obsState")
def check_subarray_obsState_idle(
    subarray_node, central_node_mid, event_recorder, command_input_factory
):
    """
    Method to check subarray is in IDLE obsState
    """
    event_recorder.subscribe_event(subarray_node.subarray_node, "obsState")
<<<<<<< HEAD
>>>>>>> 3b52eb24 (SAH-1536: Add test case for tmc-dish unavailability)

=======
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
    event_recorder.subscribe_event(subarray_node.subarray_node, "obsState")
    event_recorder.subscribe_event(
        central_node_mid.central_node, "longRunningCommandResult"
    )
<<<<<<< HEAD
>>>>>>> 05994d75 (SAH-1536: Implemented test case for unavailaity scenario)
=======
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

>>>>>>> 1de465a4 (SAH-1536: Update test case)
=======

>>>>>>> 455c6266 (SAH-1536: Implement unhappy path tests for tmc-dish pair)
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_mid", command_input_factory
    )
    pytest.command_result = central_node_mid.store_resources(assign_input_json)

    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.IDLE,
    )
<<<<<<< HEAD
=======
    event_recorder.subscribe_event(
        central_node_mid.central_node, "longRunningCommandResult"
    )
>>>>>>> 455c6266 (SAH-1536: Implement unhappy path tests for tmc-dish pair)
    assert event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "longRunningCommandResult",
        (pytest.command_result[1][0], str(ResultCode.OK.value)),
    )


@when("one of the dish subsystems CommunicationStatus is made NOT_ESTABLISHED")
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
def restart_the_dish_leaf_nodes(central_node_mid):
=======
def restart_the_dish_leaf_nodes():
>>>>>>> 1fb32fad (SAH-1536: Update test case)
    """Restart the dish leaf nodes"""
<<<<<<< HEAD

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
=======
def restart_the_dish_leaf_nodes(central_node_mid):
    """Restart the dish leaf nodes"""

    LOGGER.info("dish1 device name is: %s", spfrx_dev_name)

    check_spfrx_info = central_node_mid.dish1_db.get_device_info(
        "mid-dish/simulator-spfrx/SKA001"
    )
    LOGGER.info("spfrx device info is: %s", check_spfrx_info)
    spfrx_exported = central_node_mid.dish1_db.get_device_exported(
        "mid-dish/simulator-spfrx/SKA001"
    )
    LOGGER.info("spfrx device exported : %s", spfrx_exported)
    import tango

<<<<<<< HEAD
    central_node_mid.dish1_db.delete_device(spfrx_dev_name)
>>>>>>> 455c6266 (SAH-1536: Implement unhappy path tests for tmc-dish pair)
=======
    spfrx_proxy = tango.DeviceProxy(spfrx_exported)
    LOGGER.info("spfrx device proxy : %s", spfrx_proxy)
    central_node_mid.dish1_db.delete_device(spfrx_proxy)
>>>>>>> a773fccd (SAH-1536: Update tmc-dish unavailablity test)
    LOGGER.info("spfrx deleted")
    central_node_mid.dish1_admin_dev_proxy.RestartServer()
    # Added a wait for the completion of dish device deletion from TANGO
    # database and the dish device restart
    time.sleep(5)
<<<<<<< HEAD
=======
def restart_the_dish_leaf_nodes(tmc_mid):
=======
def restart_the_dish_leaf_nodes(tmc_mid: TMCMid):
>>>>>>> 0f512d50 (SAH-1536: Revert change)
    """Restart the dish leaf nodes"""
<<<<<<< HEAD
    tmc_mid.RestartServer("DISHLN_0")
>>>>>>> 05994d75 (SAH-1536: Implemented test case for unavailaity scenario)
=======
    tmc_mid.RestartServer("SPFRX")
>>>>>>> ea5fdb4a (SAH-1536: Updated test case)
=======
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
>>>>>>> 8ee2d95e (SAH-1536: Update test case)


@when("I configure the subarray {subarray_id}")
=======


@when(parsers.parse("I configure the subarray {subarray_id}"))
>>>>>>> 455c6266 (SAH-1536: Implement unhappy path tests for tmc-dish pair)
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
<<<<<<< HEAD
=======

>>>>>>> 455c6266 (SAH-1536: Implement unhappy path tests for tmc-dish pair)
    configure_input_json = prepare_json_args_for_commands(
        "configure_mid", command_input_factory
    )
    central_node_mid.set_subarray_id(subarray_id)
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
    pytest.command_result = subarray_node.store_configuration_data(
        configure_input_json
    )
=======
=======
>>>>>>> 455c6266 (SAH-1536: Implement unhappy path tests for tmc-dish pair)
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
<<<<<<< HEAD
>>>>>>> 3b52eb24 (SAH-1536: Add test case for tmc-dish unavailability)
=======
    pytest.command_result = subarray_node.store_configuration_data(
        configure_input_json
    )
>>>>>>> 05994d75 (SAH-1536: Implemented test case for unavailaity scenario)
=======
>>>>>>> 455c6266 (SAH-1536: Implement unhappy path tests for tmc-dish pair)
