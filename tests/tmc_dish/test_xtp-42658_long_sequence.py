<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> 00483018 (SAH-1536: Update test case)
"""Test module for long sequence functionality

This module tests the TMC-DISH long sequence functionality, ensuring that
a sequence of commands including configuration, scanning, and reconfiguration
are executed successfully and the system transitions
through the expected states.
"""
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> 438706f0 (SAH-1536: Update test case)

import ast
=======
>>>>>>> 98a5a250 (SAH-1536: Debug test failure)
=======

>>>>>>> 1fc6a549 (SAH-1536: Enable all the tmc-dish tests)
import json

import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_tango_base.control_model import ObsState

from tests.resources.test_harness.central_node_mid import CentralNodeWrapperMid
from tests.resources.test_harness.constant import COMMAND_COMPLETED
=======
"""Test module for long sequence functionality"""
=======
>>>>>>> 00483018 (SAH-1536: Update test case)

import json

import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_tango_base.control_model import ObsState

from tests.resources.test_harness.central_node_mid import CentralNodeWrapperMid
<<<<<<< HEAD
>>>>>>> 565fc8ed (SAH-1536: Add XTP numbers)
=======
from tests.resources.test_harness.constant import COMMAND_COMPLETED
>>>>>>> 00483018 (SAH-1536: Update test case)
from tests.resources.test_harness.event_recorder import EventRecorder
from tests.resources.test_harness.helpers import (
<<<<<<< HEAD
<<<<<<< HEAD
=======
    LongRunningCommandResult,
>>>>>>> 1232aef4 (SAH-1536: Resolve review comments)
=======
>>>>>>> 9e9e3c92 (SAH-1536: Resolve review comments)
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
)
from tests.resources.test_harness.subarray_node import SubarrayNodeWrapper
from tests.resources.test_harness.utils.common_utils import JsonFactory
<<<<<<< HEAD
<<<<<<< HEAD
from tests.resources.test_support.enum import DishMode, PointingState

<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
# import time


configure_logging(logging.DEBUG)
LOGGER = logging.getLogger(__name__)
=======
>>>>>>> 2ee3ddf7 (SAH-1536: Enable skipped tmc-dish tests)
=======
configure_logging(logging.DEBUG)
LOGGER = logging.getLogger(__name__)

>>>>>>> f295f999 (SAH-1564: Update test case)
=======
>>>>>>> 8f21d375 (SAH-1564: code cleanup)

<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
@pytest.mark.skip(reason="Dish pointingstate issue")
=======
@pytest.mark.skip
>>>>>>> cbe762ab (SAH-1564: Test pipline)
=======
@pytest.mark.MM
<<<<<<< HEAD
>>>>>>> f5031dbd (SAH-1564: Test pipline)
=======
@pytest.mark.skip(
    reason="Please refer "
    + "https://skao.slack.com/archives/C0625UVDVC6/p1721905870133719"
)
>>>>>>> d6a4e9e3 (SAH-1564: Test pipline)
=======
# @pytest.mark.skip(
#     reason="Please refer "
#     + "https://skao.slack.com/archives/C0625UVDVC6/p1721905870133719"
# )
<<<<<<< HEAD
@pytest.mark.MM
>>>>>>> 1f674c3b (SAH-1564: Update test case)
=======
>>>>>>> 9ef7f822 (SAH-1564: Test pipline)
=======
>>>>>>> 4c515ef0 (SAH-1564: Update test case)
=======
@pytest.mark.skip
>>>>>>> 78cca956 (SAH-1564: Update tag related changes)
=======
@pytest.mark.MM
>>>>>>> 64506083 (SAH-1564: Test long sequance test case)
=======
@pytest.mark.repeat(5)
>>>>>>> c87169cc (SAH-1564: check test case)
=======
>>>>>>> 8a66e584 (SAH-1564: Updat test case)
=======
from tests.resources.test_support.common_utils.common_helpers import Resource
=======
>>>>>>> 00483018 (SAH-1536: Update test case)
from tests.resources.test_support.enum import DishMode, PointingState


<<<<<<< HEAD
>>>>>>> 565fc8ed (SAH-1536: Add XTP numbers)
=======
@pytest.mark.skip(reason="Test being fix in SAH-1564")
>>>>>>> 00483018 (SAH-1536: Update test case)
@pytest.mark.tmc_dish
@scenario(
    "../features/tmc_dish/xtp-42658_long_sequence.feature",
    "TMC executes long sequence of commands successfully",
)
def test_tmc_dish_long_sequence_functionality():
    """
    Test case to verify TMC-DISH long sequence functionality
    """


<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
@given(
    parsers.parse(
        "a Telescope consisting of TMC, DISH {dish_ids},"
        + " simulated CSP and simulated SDP"
    )
)
def given_a_telescope(central_node_mid, dish_ids):
    """Given a TMC with DISH, CSP, and SDP

    Args:
        central_node_mid (CentralNode): A fixture for the CentralNode
        tango device class.
        dish_ids (str): A comma-separated string of dish IDs.

    This function verifies the connection to the CSP and SDP masters,
    and checks the connectivity of each dish's master and leaf node
    by sending a ping command.
    """
    assert central_node_mid.csp_master.ping() > 0
    assert central_node_mid.sdp_master.ping() > 0
    for dish_id in dish_ids.split(","):
        assert central_node_mid.dish_master_dict[dish_id].ping() > 0
        assert central_node_mid.dish_leaf_node_dict[dish_id].ping() > 0


@given("the Telescope is in ON state")
def turn_on_telescope(central_node_mid, event_recorder):
    """
    A method to put Telescope ON
    """
<<<<<<< HEAD
    for dish_id in ["SKA001", "SKA036", "SKA063", "SKA100"]:
        event_recorder.subscribe_event(
            central_node_mid.dish_master_dict[dish_id], "dishMode"
        )
        event_recorder.subscribe_event(
            central_node_mid.dish_leaf_node_dict[dish_id], "dishMode"
        )

    csp_master_sim = simulator_factory.get_or_create_simulator_device(
        SimulatorDeviceType.MID_CSP_MASTER_DEVICE
    )
    sdp_master_sim = simulator_factory.get_or_create_simulator_device(
        SimulatorDeviceType.MID_SDP_MASTER_DEVICE
    )

    event_recorder.subscribe_event(
        central_node_mid.central_node, "telescopeState"
    )
    for dish_id in ["SKA001", "SKA036", "SKA063", "SKA100"]:
        event_recorder.subscribe_event(
            central_node_mid.dish_master_dict[dish_id], "dishMode"
        )

<<<<<<< HEAD
        assert event_recorder.has_change_event_occurred(
            central_node_mid.dish_master_dict[dish_id],
            "dishMode",
            DishMode.STANDBY_LP,
        )
    Resource(central_node_mid.central_node).assert_attribute(
        "telescopeState"
    ).equals(["OFF", "STANDBY"])
=======
    event_recorder.subscribe_event(csp_master_sim, "State")
    event_recorder.subscribe_event(sdp_master_sim, "State")

=======
>>>>>>> 3b52eb24 (SAH-1536: Add test case for tmc-dish unavailability)
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
>>>>>>> 7ceda8b8 (SAH-1536: Update test case for xtp-42658)


=======
>>>>>>> aca410a8 (SAH-1536: Resolve review comments)
=======
>>>>>>> 3381f5c3 (SAH-1536: Add XTP numbers)
=======
>>>>>>> 438706f0 (SAH-1536: Update test case)
@given("TMC subarray is in IDLE obsState")
def check_subarray_obsState_idle(
    subarray_node, central_node_mid, event_recorder, command_input_factory
):
    """
    Method to check if the TMC subarray is in IDLE obsState.

    This function subscribes to the obsState event of the subarray node and
    assigns resources to the central node. It verifies that the subarray
    transitions to the IDLE obsState and that the longRunningCommandResult
    indicates a successful execution with ResultCode.OK.

    Args:
        subarray_node : A fixture for SubarrayNode tango device class
        central_node_mid : A fixture for CentralNode tango device class
        event_recorder: A fixture for EventRecorder class
        command_input_factory: A fixture for JsonFactory class
    """
    event_recorder.subscribe_event(subarray_node.subarray_node, "obsState")
<<<<<<< HEAD
<<<<<<< HEAD
    event_recorder.subscribe_event(
        subarray_node.subarray_node, "assignedResources"
    )
    event_recorder.subscribe_event(
        central_node_mid.central_node, "longRunningCommandResult"
    )
    event_recorder.subscribe_event(
        central_node_mid.central_node, "telescopeState"
    )
    central_node_mid.set_subarray_id(subarray_id)

    central_node_mid.move_to_on()
    assert event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "telescopeState",
        DevState.ON,
    )
=======
>>>>>>> 7ceda8b8 (SAH-1536: Update test case for xtp-42658)
=======
=======
@given("a telescope in OFF or STANDBY state")
def check_telescope_in_initial_state(
    central_node_mid: CentralNodeWrapperMid, event_recorder: EventRecorder
=======
@given("TMC subarray is in IDLE obsState")
def check_subarray_obsState_idle(
    subarray_node, central_node_mid, event_recorder, command_input_factory
>>>>>>> 00483018 (SAH-1536: Update test case)
):
    """
    Method to check if the TMC subarray is in IDLE obsState.

    This function subscribes to the obsState event of the subarray node and
    assigns resources to the central node. It verifies that the subarray
    transitions to the IDLE obsState and that the longRunningCommandResult
    indicates a successful execution with ResultCode.OK.

    Args:
        subarray_node : A fixture for SubarrayNode tango device class
        central_node_mid : A fixture for CentralNode tango device class
        event_recorder: A fixture for EventRecorder class
        command_input_factory: A fixture for JsonFactory class
    """
    event_recorder.subscribe_event(subarray_node.subarray_node, "obsState")
<<<<<<< HEAD
    event_recorder.subscribe_event(
        subarray_node.subarray_node, "assignedResources"
    )
    central_node_mid.set_subarray_id(subarray_id)

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
>>>>>>> 565fc8ed (SAH-1536: Add XTP numbers)
<<<<<<< HEAD
>>>>>>> 3381f5c3 (SAH-1536: Add XTP numbers)
=======
=======
>>>>>>> 00483018 (SAH-1536: Update test case)
>>>>>>> 438706f0 (SAH-1536: Update test case)

    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_mid", command_input_factory
    )
<<<<<<< HEAD
<<<<<<< HEAD
    pytest.command_result = central_node_mid.store_resources(assign_input_json)
=======
    central_node_mid.store_resources(assign_input_json)
>>>>>>> 565fc8ed (SAH-1536: Add XTP numbers)
=======
    pytest.command_result = central_node_mid.store_resources(assign_input_json)
>>>>>>> 00483018 (SAH-1536: Update test case)

    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.IDLE,
    )
<<<<<<< HEAD
<<<<<<< HEAD
=======
<<<<<<< HEAD
=======
<<<<<<< HEAD
=======
>>>>>>> 00483018 (SAH-1536: Update test case)
>>>>>>> 438706f0 (SAH-1536: Update test case)
    event_recorder.subscribe_event(
        central_node_mid.central_node, "longRunningCommandResult"
    )
>>>>>>> 3381f5c3 (SAH-1536: Add XTP numbers)
    assert event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "longRunningCommandResult",
        (pytest.command_result[1][0], COMMAND_COMPLETED),
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
=======
=======
        (pytest.command_result[1][0], str(ResultCode.OK.value)),
    )
    assert subarray_node.subarray_node.assignedResources == ast.literal_eval(
        resources
>>>>>>> a2ee3172 (SAH-1536: Implemented test case for unavailaity scenario)
>>>>>>> d4e73adf (SAH-1536: Implemented test case for unavailaity scenario)
=======
>>>>>>> f8f727f6 (SAH-1536: Updated test case)
    )
<<<<<<< HEAD
    assert subarray_node.subarray_node.assignedResources == ast.literal_eval(
        resources
    )
=======
=======
    LOGGER.info(
        f"Assigned Resources: {subarray_node.subarray_node.assignedResources}"
    )
    LOGGER.info(f"Resources:{resources}")
    LOGGER.info(f"Resources convert:{ast.literal_eval(resources)}")
    # assert event_recorder.has_change_event_occurred(
    #     subarray_node.subarray_node,
    #     "assignedResources",
    #     ast.literal_eval(resources),  # casts string coded tuple to tuple
    # )
>>>>>>> 565fc8ed (SAH-1536: Add XTP numbers)
<<<<<<< HEAD
>>>>>>> 3381f5c3 (SAH-1536: Add XTP numbers)
=======
=======
    )
>>>>>>> 00483018 (SAH-1536: Update test case)
>>>>>>> 438706f0 (SAH-1536: Update test case)


@when(
    parsers.parse(
<<<<<<< HEAD
<<<<<<< HEAD
        "I configure the subarray {subarray_id} with {receiver_band_1}"
=======
        "I configure the subarray {subarray_id} with receiver_band_1"
>>>>>>> 565fc8ed (SAH-1536: Add XTP numbers)
=======
        "I configure the subarray {subarray_id} with {receiver_band_1}"
>>>>>>> 00483018 (SAH-1536: Update test case)
    )
)
def configure_subarray(
    subarray_node: SubarrayNodeWrapper,
    central_node_mid: CentralNodeWrapperMid,
    event_recorder: EventRecorder,
    command_input_factory: JsonFactory,
    subarray_id: str,
<<<<<<< HEAD
<<<<<<< HEAD
    receiver_band_1: str,
):
    """
    A method to invoke first Configure command

    Args:
        subarray_node: Fixture for a Subarray Node wrapper class
        central_node_mid: Fixture for a TMC CentralNode wrapper class
        event_recorder: Fixture for EventRecorder class
        command_input_factory: fixture for creating input required
        for command
        subarray_id (str): Subarray ID
        receiver_band_1 (str): receiver band 1 for configure command
    """
    event_recorder.subscribe_event(
        subarray_node.subarray_node, "longRunningCommandResult"
    )
=======
=======
    receiver_band_1: str,
>>>>>>> 00483018 (SAH-1536: Update test case)
):
    """
    A method to invoke first Configure command

    Args:
        subarray_node: Fixture for a Subarray Node wrapper class
        central_node_mid: Fixture for a TMC CentralNode wrapper class
        event_recorder: Fixture for EventRecorder class
        command_input_factory: fixture for creating input required
        for command
        subarray_id (str): Subarray ID
        receiver_band_1 (str): receiver band 1 for configure command
    """
<<<<<<< HEAD
>>>>>>> 565fc8ed (SAH-1536: Add XTP numbers)
=======
    event_recorder.subscribe_event(
        subarray_node.subarray_node, "longRunningCommandResult"
    )
>>>>>>> 00483018 (SAH-1536: Update test case)
    input_json = prepare_json_args_for_commands(
        "configure_mid", command_input_factory
    )
    configure_input_json = json.loads(input_json)
<<<<<<< HEAD
<<<<<<< HEAD
    configure_input_json["dish"]["receiver_band"] = receiver_band_1
    configure_input_json["csp"]["common"]["frequency_band"] = "1"
    central_node_mid.set_subarray_id(subarray_id)
    pytest.command_result = subarray_node.store_configuration_data(
        json.dumps(configure_input_json)
    )
    for dish_id in ["SKA001", "SKA036", "SKA063", "SKA100"]:
<<<<<<< HEAD
<<<<<<< HEAD
        event_recorder.subscribe_event(
            central_node_mid.dish_master_dict[dish_id], "pointingState"
        )
        event_recorder.subscribe_event(
<<<<<<< HEAD
            central_node_mid.dish_master_dict[dish_id], "dishMode"
=======
            central_node_mid.dish_leaf_node_dict[dish_id], "pointingState"
>>>>>>> 2ee3ddf7 (SAH-1536: Enable skipped tmc-dish tests)
        )

=======
>>>>>>> 3f2e08b9 (SAH-1536: Resolve review comments)
=======
        event_recorder.subscribe_event(
            central_node_mid.dish_leaf_node_dict[dish_id],
            "longRunningCommandResult",
        )
<<<<<<< HEAD
>>>>>>> d6082288 (SAH-1536: Update tmc-dish long sequence test)
=======
=======
    configure_input_json["dish"]["receiver_band"] = "1"
=======
    configure_input_json["dish"]["receiver_band"] = receiver_band_1
    configure_input_json["csp"]["common"]["frequency_band"] = "1"
>>>>>>> 00483018 (SAH-1536: Update test case)
    central_node_mid.set_subarray_id(subarray_id)
    pytest.command_result = subarray_node.store_configuration_data(
        json.dumps(configure_input_json)
    )
    for dish_id in ["SKA001", "SKA036", "SKA063", "SKA100"]:
        event_recorder.subscribe_event(
            central_node_mid.dish_leaf_node_dict[dish_id],
            "longRunningCommandResult",
        )
<<<<<<< HEAD
        event_recorder.subscribe_event(
            central_node_mid.dish_master_dict[dish_id], "dishMode"
        )

>>>>>>> 565fc8ed (SAH-1536: Add XTP numbers)
<<<<<<< HEAD
>>>>>>> 3381f5c3 (SAH-1536: Add XTP numbers)
=======
=======
>>>>>>> 00483018 (SAH-1536: Update test case)
>>>>>>> 438706f0 (SAH-1536: Update test case)
        assert event_recorder.has_change_event_occurred(
            central_node_mid.dish_master_dict[dish_id],
            "dishMode",
            DishMode.OPERATE,
<<<<<<< HEAD
<<<<<<< HEAD
        )

=======
<<<<<<< HEAD
=======
<<<<<<< HEAD
=======
>>>>>>> 00483018 (SAH-1536: Update test case)
>>>>>>> 438706f0 (SAH-1536: Update test case)
            lookahead=10,
        )
        assert event_recorder.has_change_event_occurred(
            central_node_mid.dish_leaf_node_dict[dish_id],
            "dishMode",
            DishMode.OPERATE,
            lookahead=10,
<<<<<<< HEAD
        )
=======
        )

>>>>>>> 565fc8ed (SAH-1536: Add XTP numbers)
<<<<<<< HEAD
>>>>>>> 3381f5c3 (SAH-1536: Add XTP numbers)
=======
=======
        )
>>>>>>> 00483018 (SAH-1536: Update test case)
>>>>>>> 438706f0 (SAH-1536: Update test case)
        assert event_recorder.has_change_event_occurred(
            central_node_mid.dish_master_dict[dish_id],
            "pointingState",
            PointingState.TRACK,
<<<<<<< HEAD
<<<<<<< HEAD
=======
<<<<<<< HEAD
=======
<<<<<<< HEAD
=======
>>>>>>> 00483018 (SAH-1536: Update test case)
>>>>>>> 438706f0 (SAH-1536: Update test case)
            lookahead=10,
        )
        assert event_recorder.has_change_event_occurred(
            central_node_mid.dish_leaf_node_dict[dish_id],
            "pointingState",
            PointingState.TRACK,
            lookahead=10,
<<<<<<< HEAD
=======
>>>>>>> 565fc8ed (SAH-1536: Add XTP numbers)
<<<<<<< HEAD
>>>>>>> 3381f5c3 (SAH-1536: Add XTP numbers)
=======
=======
>>>>>>> 00483018 (SAH-1536: Update test case)
>>>>>>> 438706f0 (SAH-1536: Update test case)
        )
        logging.info(
            "longRunningCommandResult for DishLN after configure1 %s",
            central_node_mid.dish_leaf_node_dict[
                dish_id
            ].longRunningCommandResult,
        )
        logging.info("pytest.command_result1: %s", str(pytest.command_result))
        assert event_recorder.has_change_event_occurred(
            central_node_mid.dish_leaf_node_dict[dish_id],
            "longRunningCommandResult",
            (pytest.command_result[1][0], str(ResultCode.OK.value)),
            lookahead=15,
        )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
<<<<<<< HEAD
<<<<<<< HEAD
        ObsState.READY,
<<<<<<< HEAD
<<<<<<< HEAD
        lookahead=15,
=======
<<<<<<< HEAD
        lookahead=10,
=======
        lookahead=12,
>>>>>>> b34bdecd (SAH-1536: Update test case.)
>>>>>>> 454adc68 (SAH-1536: Update test case.)
=======
        lookahead=10,
>>>>>>> fe16fe96 (SAH-1536: Update test case.)
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "longRunningCommandResult",
        (pytest.command_result[1][0], COMMAND_COMPLETED),
=======
        ObsState.CONFIGURING,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.READY,
>>>>>>> 565fc8ed (SAH-1536: Add XTP numbers)
=======
        ObsState.READY,
        lookahead=10,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "longRunningCommandResult",
        (pytest.command_result[1][0], COMMAND_COMPLETED),
>>>>>>> 00483018 (SAH-1536: Update test case)
    )


@when(parsers.parse("I issue End command to the subarray {subarray_id}"))
def end_configuration_on_subarray(
    subarray_node: SubarrayNodeWrapper,
    central_node_mid: CentralNodeWrapperMid,
    event_recorder: EventRecorder,
    subarray_id: str,
):
    """
    A method to invoke end command
<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> 00483018 (SAH-1536: Update test case)

    Args:
        subarray_node: Fixture for a Subarray Node wrapper class
        central_node_mid: Fixture for a TMC CentralNode wrapper class
        event_recorder: Fixture for EventRecorder class
        subarray_id (str): Subarray ID
<<<<<<< HEAD
    """
    event_recorder.subscribe_event(
        subarray_node.subarray_node, "longRunningCommandResult"
    )
    central_node_mid.set_subarray_id(subarray_id)
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
    pytest.command_result = subarray_node.end_observation()
=======
    pytest.command_result = subarray_node.execute_transition("End")
>>>>>>> 1232aef4 (SAH-1536: Resolve review comments)
=======
    pytest.command_result = subarray_node.end_observation()
>>>>>>> 091f5628 (SAH-1536: Update test case.)
=======
    pytest.command_result = subarray_node.execute_transition("End")
>>>>>>> a3a8fb20 (SAH-1536: Update the test case.)
    for dish_id in ["SKA001", "SKA036", "SKA063", "SKA100"]:
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
        event_recorder.subscribe_event(
            central_node_mid.dish_master_dict[dish_id], "dishMode"
=======
        logging.info(
            "DISHMODE for Dish after end %s: %s",
            dish_id,
            central_node_mid.dish_master_dict[dish_id].dishMode,
        )
        logging.info(
            "DISHMODE for DishLN after end %s: %s",
            dish_id,
            central_node_mid.dish_leaf_node_dict[dish_id].dishMode,
        )
        logging.info(
            "pointingState for Dish after end %s: %s",
            dish_id,
            central_node_mid.dish_master_dict[dish_id].pointingState,
        )
        logging.info(
            "pointingState for DishLN after end %s: %s",
            dish_id,
            central_node_mid.dish_leaf_node_dict[dish_id].pointingState,
        )
        # assert event_recorder.has_change_event_occurred(
        #     central_node_mid.dish_master_dict[dish_id],
        #     "dishMode",
        #     DishMode.STANDBY_FP,
        #     lookahead=10,
        # )
        # assert event_recorder.has_change_event_occurred(
        #     central_node_mid.dish_leaf_node_dict[dish_id],
        #     "dishMode",
        #     DishMode.STANDBY_FP,
        #     lookahead=10,
        # )
=======

>>>>>>> 2ee3ddf7 (SAH-1536: Enable skipped tmc-dish tests)
=======
>>>>>>> 81ad2993 (SAH-1536: Test tmc-dish long sequence tests)
=======

>>>>>>> 0029e631 (SAH-1536: Update test case for xtp-42658)
        assert event_recorder.has_change_event_occurred(
            central_node_mid.dish_master_dict[dish_id],
            "pointingState",
            PointingState.READY,
            lookahead=10,
        )
        assert event_recorder.has_change_event_occurred(
            central_node_mid.dish_leaf_node_dict[dish_id],
            "pointingState",
            PointingState.READY,
            lookahead=10,
>>>>>>> 1a8aefae (SAH-1536: Test tmc-dish long sequence tests)
        )

<<<<<<< HEAD
=======
=======
=======
>>>>>>> 00483018 (SAH-1536: Update test case)
    """
    central_node_mid.set_subarray_id(subarray_id)
    pytest.command_result = subarray_node.execute_transition("End")
    for dish_id in ["SKA001", "SKA036", "SKA063", "SKA100"]:

>>>>>>> 3381f5c3 (SAH-1536: Add XTP numbers)
        assert event_recorder.has_change_event_occurred(
            central_node_mid.dish_master_dict[dish_id],
<<<<<<< HEAD
            "dishMode",
            DishMode.STANDBY_FP,
<<<<<<< HEAD
            lookahead=12,
        )
=======
=======
            "pointingState",
            PointingState.READY,
            lookahead=10,
>>>>>>> 438706f0 (SAH-1536: Update test case)
        )
<<<<<<< HEAD
>>>>>>> 565fc8ed (SAH-1536: Add XTP numbers)
<<<<<<< HEAD
>>>>>>> 3381f5c3 (SAH-1536: Add XTP numbers)
=======
=======
        assert event_recorder.has_change_event_occurred(
            central_node_mid.dish_leaf_node_dict[dish_id],
            "pointingState",
            PointingState.READY,
            lookahead=10,
        )

>>>>>>> 00483018 (SAH-1536: Update test case)
>>>>>>> 438706f0 (SAH-1536: Update test case)
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.IDLE,
    )

<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> 00483018 (SAH-1536: Update test case)
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "longRunningCommandResult",
        (pytest.command_result[1][0], COMMAND_COMPLETED),
    )

<<<<<<< HEAD

@when(
    parsers.parse(
        "I reconfigure subarray {subarray_id} with {receiver_band_2}"
    )
=======

@when(
    parsers.parse("I reconfigure subarray {subarray_id} with receiver_band 2")
>>>>>>> 565fc8ed (SAH-1536: Add XTP numbers)
=======

@when(
    parsers.parse(
        "I reconfigure subarray {subarray_id} with {receiver_band_2}"
    )
>>>>>>> 00483018 (SAH-1536: Update test case)
)
def reconfigure_subarray(
    subarray_node: SubarrayNodeWrapper,
    central_node_mid: CentralNodeWrapperMid,
    event_recorder: EventRecorder,
    command_input_factory: JsonFactory,
    subarray_id: str,
<<<<<<< HEAD
<<<<<<< HEAD
    receiver_band_2: str,
):
    """
    A method to invoke second Configure command

    Args:
        subarray_node: Fixture for a Subarray Node wrapper class
        central_node_mid: Fixture for a TMC CentralNode wrapper class
        event_recorder: Fixture for EventRecorder class
        subarray_id (str): Subarray ID
        receiver_band_1 (str): receiver band 1 for configure command
    """
    event_recorder.subscribe_event(
        subarray_node.subarray_node, "longRunningCommandResult"
    )
=======
=======
    receiver_band_2: str,
>>>>>>> 00483018 (SAH-1536: Update test case)
):
    """
    A method to invoke second Configure command

    Args:
        subarray_node: Fixture for a Subarray Node wrapper class
        central_node_mid: Fixture for a TMC CentralNode wrapper class
        event_recorder: Fixture for EventRecorder class
        subarray_id (str): Subarray ID
        receiver_band_1 (str): receiver band 1 for configure command
    """
<<<<<<< HEAD
>>>>>>> 565fc8ed (SAH-1536: Add XTP numbers)
=======
    event_recorder.subscribe_event(
        subarray_node.subarray_node, "longRunningCommandResult"
    )
>>>>>>> 00483018 (SAH-1536: Update test case)
    input_json = prepare_json_args_for_commands(
        "configure_mid", command_input_factory
    )
    configure_input_json = json.loads(input_json)
<<<<<<< HEAD
<<<<<<< HEAD
    configure_input_json["dish"]["receiver_band"] = receiver_band_2
    configure_input_json["csp"]["common"]["frequency_band"] = "2"
    central_node_mid.set_subarray_id(subarray_id)
    pytest.command_result = subarray_node.execute_transition(
        "Configure", json.dumps(configure_input_json)
    )
    for dish_id in ["SKA001", "SKA036", "SKA063", "SKA100"]:
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
        event_recorder.subscribe_event(
            central_node_mid.dish_master_dict[dish_id], "pointingState"
        )
        event_recorder.subscribe_event(
            central_node_mid.dish_master_dict[dish_id], "dishMode"
        )
<<<<<<< HEAD

        assert event_recorder.has_change_event_occurred(
            central_node_mid.dish_master_dict[dish_id],
            "dishMode",
            DishMode.OPERATE,
            lookahead=16,
        )

=======
=======

>>>>>>> 2ee3ddf7 (SAH-1536: Enable skipped tmc-dish tests)
=======
=======
        LOGGER.info("current dish id: %s", dish_id)
>>>>>>> f295f999 (SAH-1564: Update test case)
=======
>>>>>>> 8f21d375 (SAH-1564: code cleanup)
        event_recorder.subscribe_event(
            central_node_mid.dish_leaf_node_dict[dish_id],
            "longRunningCommandResult",
        )
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
>>>>>>> d6082288 (SAH-1536: Update tmc-dish long sequence test)
        assert (
            central_node_mid.dish_master_dict[dish_id].dishMode
            == DishMode.OPERATE
=======
        # assert (
        #     central_node_mid.dish_master_dict[dish_id].dishMode
        #     == DishMode.OPERATE
        # )
        # assert (
        #     central_node_mid.dish_leaf_node_dict[dish_id].dishMode
        #     == DishMode.OPERATE
        # )
=======
>>>>>>> 5f723990 (SAH-1564: Test pipline)
=======
=======
    configure_input_json["dish"]["receiver_band"] = "2"
=======
    configure_input_json["dish"]["receiver_band"] = receiver_band_2
    configure_input_json["csp"]["common"]["frequency_band"] = "2"
>>>>>>> 00483018 (SAH-1536: Update test case)
    central_node_mid.set_subarray_id(subarray_id)
    pytest.command_result = subarray_node.execute_transition(
        "Configure", json.dumps(configure_input_json)
    )

    for dish_id in ["SKA001", "SKA036", "SKA063", "SKA100"]:
        event_recorder.subscribe_event(
            central_node_mid.dish_leaf_node_dict[dish_id],
            "longRunningCommandResult",
        )
<<<<<<< HEAD
        event_recorder.subscribe_event(
            central_node_mid.dish_master_dict[dish_id], "dishMode"
        )

>>>>>>> 565fc8ed (SAH-1536: Add XTP numbers)
<<<<<<< HEAD
>>>>>>> 3381f5c3 (SAH-1536: Add XTP numbers)
=======
=======
>>>>>>> 00483018 (SAH-1536: Update test case)
>>>>>>> 438706f0 (SAH-1536: Update test case)
        assert event_recorder.has_change_event_occurred(
            central_node_mid.dish_master_dict[dish_id],
            "dishMode",
            DishMode.OPERATE,
<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> 00483018 (SAH-1536: Update test case)
            lookahead=10,
>>>>>>> 54f35f81 (SAH-1564: Update test case)
        )
        assert event_recorder.has_change_event_occurred(
            central_node_mid.dish_leaf_node_dict[dish_id],
            "dishMode",
            DishMode.OPERATE,
            lookahead=10,
<<<<<<< HEAD
        )
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
        # assert event_recorder.has_change_event_occurred(
        #     central_node_mid.dish_master_dict[dish_id],
        #     "dishMode",
        #     DishMode.OPERATE,
        #     lookahead=10,
        # )
        # assert event_recorder.has_change_event_occurred(
        #     central_node_mid.dish_leaf_node_dict[dish_id],
        #     "dishMode",
        #     DishMode.OPERATE,
        #     lookahead=10,
        # )
>>>>>>> 752c8d76 (SAH-1536: Update test case for xtp-42658)
=======

>>>>>>> 2ee3ddf7 (SAH-1536: Enable skipped tmc-dish tests)
=======
>>>>>>> 54f35f81 (SAH-1564: Update test case)
=======
=======
            lookahead=16,
        )

>>>>>>> 565fc8ed (SAH-1536: Add XTP numbers)
<<<<<<< HEAD
>>>>>>> 3381f5c3 (SAH-1536: Add XTP numbers)
=======
=======
        )
>>>>>>> 00483018 (SAH-1536: Update test case)
>>>>>>> 438706f0 (SAH-1536: Update test case)
        assert event_recorder.has_change_event_occurred(
            central_node_mid.dish_master_dict[dish_id],
            "pointingState",
            PointingState.TRACK,
<<<<<<< HEAD
<<<<<<< HEAD
=======
<<<<<<< HEAD
=======
>>>>>>> 3381f5c3 (SAH-1536: Add XTP numbers)
=======
>>>>>>> 00483018 (SAH-1536: Update test case)
>>>>>>> 438706f0 (SAH-1536: Update test case)
            lookahead=15,
        )
        assert event_recorder.has_change_event_occurred(
            central_node_mid.dish_leaf_node_dict[dish_id],
            "pointingState",
            PointingState.TRACK,
<<<<<<< HEAD
            lookahead=10,
>>>>>>> a1513bbc (SAH-1564: code cleanup)
=======
            lookahead=15,
<<<<<<< HEAD
<<<<<<< HEAD
>>>>>>> c8da6868 (SAH-1564: increase lookahead)
=======
=======
>>>>>>> 565fc8ed (SAH-1536: Add XTP numbers)
>>>>>>> 3381f5c3 (SAH-1536: Add XTP numbers)
=======
=======
>>>>>>> 565fc8ed (SAH-1536: Add XTP numbers)
=======
>>>>>>> 00483018 (SAH-1536: Update test case)
>>>>>>> 438706f0 (SAH-1536: Update test case)
        )
        logging.info(
            "longRunningCommandResult for DishLN after configure2 %s",
            central_node_mid.dish_leaf_node_dict[
                dish_id
            ].longRunningCommandResult,
        )
        logging.info("pytest.command_result2: %s", str(pytest.command_result))
        assert event_recorder.has_change_event_occurred(
            central_node_mid.dish_leaf_node_dict[dish_id],
            "longRunningCommandResult",
            (pytest.command_result[1][0], str(ResultCode.OK.value)),
            lookahead=15,
        )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
<<<<<<< HEAD
<<<<<<< HEAD
        ObsState.READY,
        lookahead=15,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "longRunningCommandResult",
        (pytest.command_result[1][0], COMMAND_COMPLETED),
=======
        ObsState.CONFIGURING,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.READY,
>>>>>>> 565fc8ed (SAH-1536: Add XTP numbers)
=======
        ObsState.READY,
        lookahead=15,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "longRunningCommandResult",
        (pytest.command_result[1][0], COMMAND_COMPLETED),
>>>>>>> 00483018 (SAH-1536: Update test case)
    )


@when(parsers.parse("I issue scan command with {scan_id} on subarray"))
def invoke_scan(
    central_node_mid: CentralNodeWrapperMid,
    subarray_node: SubarrayNodeWrapper,
    command_input_factory: JsonFactory,
    event_recorder: EventRecorder,
    scan_id: str,
):
    """
    A method to invoke Scan command
<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> 00483018 (SAH-1536: Update test case)

    Args:
        central_node_mid: Fixture for a TMC CentralNode wrapper class
        subarray_node: Fixture for a Subarray Node wrapper class
        command_input_factory: fixture for creating input required
        for command
        event_recorder: Fixture for EventRecorder class
        scan_id (str): scan id for DISH components
<<<<<<< HEAD
=======
>>>>>>> 565fc8ed (SAH-1536: Add XTP numbers)
=======
>>>>>>> 00483018 (SAH-1536: Update test case)
    """
    scan_input_json = prepare_json_args_for_commands(
        "scan_mid", command_input_factory
    )
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
    subarray_node.store_scan_data(scan_input_json)
=======
=======
>>>>>>> 3381f5c3 (SAH-1536: Add XTP numbers)
=======
=======
>>>>>>> 00483018 (SAH-1536: Update test case)
>>>>>>> 438706f0 (SAH-1536: Update test case)

    pytest.command_result = subarray_node.execute_transition(
        "Scan", scan_input_json
    )
<<<<<<< HEAD
<<<<<<< HEAD
>>>>>>> 9e9e3c92 (SAH-1536: Resolve review comments)
=======
=======
    subarray_node.execute_transition("Scan", scan_input_json)
>>>>>>> 565fc8ed (SAH-1536: Add XTP numbers)
>>>>>>> 3381f5c3 (SAH-1536: Add XTP numbers)
=======
=======
    subarray_node.execute_transition("Scan", scan_input_json)
>>>>>>> 565fc8ed (SAH-1536: Add XTP numbers)
=======
>>>>>>> 00483018 (SAH-1536: Update test case)
>>>>>>> 438706f0 (SAH-1536: Update test case)

    for dish_id in ["SKA001", "SKA036", "SKA063", "SKA100"]:
        event_recorder.subscribe_event(
            central_node_mid.dish_master_dict[dish_id], "scanID"
        )
        event_recorder.subscribe_event(
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
            central_node_mid.dish_master_dict[dish_id], "pointingState"
        )
        event_recorder.subscribe_event(
            central_node_mid.dish_master_dict[dish_id], "dishMode"
=======
=======
>>>>>>> 3381f5c3 (SAH-1536: Add XTP numbers)
=======
>>>>>>> 438706f0 (SAH-1536: Update test case)
            central_node_mid.dish_master_dict[dish_id],
            "longRunningCommandResult",
        )
        event_recorder.subscribe_event(
            central_node_mid.dish_leaf_node_dict[dish_id],
            "longRunningCommandResult",
<<<<<<< HEAD
>>>>>>> e299607f (SAH-1536: Resolve review comments)
=======
=======
            central_node_mid.dish_master_dict[dish_id], "pointingState"
        )
        event_recorder.subscribe_event(
            central_node_mid.dish_master_dict[dish_id], "dishMode"
>>>>>>> 565fc8ed (SAH-1536: Add XTP numbers)
<<<<<<< HEAD
>>>>>>> 3381f5c3 (SAH-1536: Add XTP numbers)
=======
=======
            central_node_mid.dish_master_dict[dish_id],
            "longRunningCommandResult",
        )
        event_recorder.subscribe_event(
            central_node_mid.dish_leaf_node_dict[dish_id],
            "longRunningCommandResult",
>>>>>>> 00483018 (SAH-1536: Update test case)
>>>>>>> 438706f0 (SAH-1536: Update test case)
        )
        assert event_recorder.has_change_event_occurred(
            central_node_mid.dish_master_dict[dish_id],
            "scanID",
            scan_id,
        )

        assert (
            central_node_mid.dish_master_dict[dish_id].dishMode
            == DishMode.OPERATE
        )
<<<<<<< HEAD
<<<<<<< HEAD
=======
<<<<<<< HEAD
=======
<<<<<<< HEAD
=======
>>>>>>> 00483018 (SAH-1536: Update test case)
>>>>>>> 438706f0 (SAH-1536: Update test case)
        assert (
            central_node_mid.dish_leaf_node_dict[dish_id].dishMode
            == DishMode.OPERATE
        )
<<<<<<< HEAD
=======
>>>>>>> 565fc8ed (SAH-1536: Add XTP numbers)
<<<<<<< HEAD
>>>>>>> 3381f5c3 (SAH-1536: Add XTP numbers)
=======
=======
>>>>>>> 00483018 (SAH-1536: Update test case)
>>>>>>> 438706f0 (SAH-1536: Update test case)

        assert (
            central_node_mid.dish_master_dict[dish_id].pointingState
            == PointingState.TRACK
        )
<<<<<<< HEAD
<<<<<<< HEAD
=======
<<<<<<< HEAD
=======
>>>>>>> 3381f5c3 (SAH-1536: Add XTP numbers)
=======
>>>>>>> 00483018 (SAH-1536: Update test case)
>>>>>>> 438706f0 (SAH-1536: Update test case)
        assert (
            central_node_mid.dish_leaf_node_dict[dish_id].pointingState
            == PointingState.TRACK
        )
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
        logging.info(
            "longRunningCommandResult for DishLN after scan %s",
            central_node_mid.dish_leaf_node_dict[
                dish_id
            ].longRunningCommandResult,
        )
<<<<<<< HEAD
        logging.info(
            "longRunningCommandResult for DISHmaster after scan %s",
            central_node_mid.dish_master_dict[
                dish_id
            ].longRunningCommandResult,
        )
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
=======
        time.sleep(10)
=======
        time.sleep(20)
>>>>>>> 59e38b4d (SAH-1536: Debug test failure)
        logging.info(
            "longRunningCommandResult for DishLN after scan and sleep %s",
            central_node_mid.dish_leaf_node_dict[
                dish_id
            ].longRunningCommandResult,
        )
        logging.info(
            "longRunningCommandResult for DISHmaster after scan and sleep %s",
            central_node_mid.dish_master_dict[
                dish_id
            ].longRunningCommandResult,
        )
>>>>>>> 98a5a250 (SAH-1536: Debug test failure)
=======
>>>>>>> 3d6be7fc (SAH-1536: Debug test failure)
        assert event_recorder.has_change_event_occurred(
            central_node_mid.dish_master_dict[dish_id],
            "longRunningCommandResult",
            (pytest.command_result[1][0], str(ResultCode.OK.value)),
        )
=======
        logging.info("pytest.command_result: %s", str(pytest.command_result))
>>>>>>> 09c4fc92 (SAH-1536: Debug test failure)
        assert event_recorder.has_change_event_occurred(
            central_node_mid.dish_leaf_node_dict[dish_id],
            "longRunningCommandResult",
            (pytest.command_result[1][0], str(ResultCode.OK.value)),
            lookahead=15,
        )
<<<<<<< HEAD
>>>>>>> 1232aef4 (SAH-1536: Resolve review comments)
=======
        # assert event_recorder.has_change_event_occurred(
        #     central_node_mid.dish_leaf_node_dict[dish_id],
        #     "longRunningCommandResult",
        #     (pytest.command_result[1][0], str(ResultCode.OK.value)),
        # )
>>>>>>> 1003daaa (SAH-1536: Resolve review comments)
=======
>>>>>>> 98a5a250 (SAH-1536: Debug test failure)
=======
>>>>>>> 0031d69e (SAH-1536: Test pipeline)
=======
=======
>>>>>>> 565fc8ed (SAH-1536: Add XTP numbers)
>>>>>>> 3381f5c3 (SAH-1536: Add XTP numbers)
=======
=======
>>>>>>> 565fc8ed (SAH-1536: Add XTP numbers)
=======
>>>>>>> 00483018 (SAH-1536: Update test case)
>>>>>>> 438706f0 (SAH-1536: Update test case)


@then("tmc subarraynode reports SCANNING obsState")
def check_tmc_subarray_scanning(
    subarray_node: SubarrayNodeWrapper,
    event_recorder: EventRecorder,
):
<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> 00483018 (SAH-1536: Update test case)
    """Checks if SubarrayNode's obsState attribute value is SCANNING

    Args:
        subarray_node: Fixture for a Subarray Node wrapper class
        event_recorder: Fixture for EventRecorder class
    """
<<<<<<< HEAD
=======
    """Checks if SubarrayNode's obsState attribute value is SCANNING"""
>>>>>>> 565fc8ed (SAH-1536: Add XTP numbers)
=======
>>>>>>> 00483018 (SAH-1536: Update test case)
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.SCANNING,
    )
<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> 00483018 (SAH-1536: Update test case)
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.READY,
        lookahead=10,
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
    )
<<<<<<< HEAD
=======
>>>>>>> 565fc8ed (SAH-1536: Add XTP numbers)
=======
>>>>>>> 00483018 (SAH-1536: Update test case)
=======
    )
>>>>>>> 7714cfbb (SAH-1536: Update test case for xtp-42658)
=======
    )
>>>>>>> e4547cde (SAH-1536: Update test case for xtp-42658)
=======
    )
>>>>>>> 4a3d3a1e (SAH-1536: Add test case for tmc-dish unavailability)
=======
    )
>>>>>>> 6806ec97 (SAH-1536: Enable skipped tmc-dish tests)
