"""
Test case to validate negative scenario for
   Dish Vcc map configuration feature
"""
import pytest
from pytest_bdd import given, parsers, scenario, then, when
from tango import DevState

from tests.resources.test_harness.constant import (
    ERROR_PROPAGATION_DEFECT,
    RESET_DEFECT,
)
from tests.resources.test_harness.helpers import (
    prepare_json_args_for_centralnode_commands,
)
from tests.resources.test_harness.utils.enums import SimulatorDeviceType
from tests.resources.test_support.common_utils.result_code import ResultCode

# TODO This test case fails frequently with corba exception
# @pytest.mark.skip("Need design change to avoid timeout corba exception")


@pytest.mark.skip(
    reason="Test fails because of TRANSIENT CORBA EXCEPTION with command"
    + " exceeding the timeout of 3 seconds"
)
@pytest.mark.SKA_mid
@scenario(
    "../features/load_dish_cfg_command_negative_scenario.feature",
    "TMC returns error message when non existent file is provided "
    "in configuration",
)
def test_central_node_return_error_for_invalid_file():
    """This test validate that when non existent file
    provided in dish vcc configuration json then command is rejected
    with error
    Glossary:
    - "central_node_mid": fixture for a TMC CentralNode Mid under test
    which provides simulated master devices
    - "event_recorder": fixture for a MockTangoEventCallbackGroup
    for validating the subscribing and receiving events.
    - "simulator_factory": fixture for creating simulator devices for
    mid Telescope respectively.
    """


@pytest.mark.skip(
    reason="Test fails because of TRANSIENT CORBA EXCEPTION with command"
    + " exceeding the timeout of 3 seconds"
)
@pytest.mark.SKA_mid
@scenario(
    "../features/load_dish_cfg_command_negative_scenario.feature",
    "TMC returns error when invalid dish id is provided in configuration",
)
def test_central_node_return_error_for_invalid_dish_id():
    """This test validate that when invalid dish id provided
    in dish vcc map json then command is rejected with error
    """


@pytest.mark.skip(
    reason="Test fails because of TRANSIENT CORBA EXCEPTION with command"
    + " exceeding the timeout of 3 seconds"
)
@pytest.mark.SKA_mid
@scenario(
    "../features/load_dish_cfg_command_negative_scenario.feature",
    "TMC returns error when duplicate vcc id is provided in configuration",
)
def test_central_node_return_error_for_duplicate_vcc_id():
    """This test validate that when duplicate vcc id provided
    in dish vcc map json then command is rejected with error
    """


@pytest.mark.skip(
    reason="Test fails because of TRANSIENT CORBA EXCEPTION with command"
    + " exceeding the timeout of 3 seconds"
)
@pytest.mark.SKA_mid
@pytest.mark.skip(
    reason="This will be enable once Dish Vcc feature is integrate."
)
@scenario(
    "../features/load_dish_cfg_command_negative_scenario.feature",
    "TMC handling exception from CSP Subarray",
)
def test_central_node_handle_exception():
    """This test validate that when exception is raised on csp controller
    device then the csp master should raise the error to central node and
    sysParam and sourceSysParam attributes are not updated at csp master leaf
    node device
    """


@given("a TMC")
def given_tmc():
    """Given a TMC"""


@given("Telescope is in ON state")
def telescope_in_on_state(central_node_mid, event_recorder):
    """Move Telescope to ON state"""
    event_recorder.subscribe_event(
        central_node_mid.central_node, "telescopeState"
    )
    central_node_mid.move_to_on()
    assert event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "telescopeState",
        DevState.ON,
    )


@when(
    parsers.parse(
        "I issue the command LoadDishCfg on TMC with non "
        "existent file {file_name} in configuration"
    )
)
def invoke_load_dish_cfg(central_node_mid, command_input_factory, file_name):
    """Call load_dish_cfg method which invoke LoadDishCfg
    command on CentralNode
    """
    # Prepare input for load dish configuration
    load_dish_cfg_json = prepare_json_args_for_centralnode_commands(
        f"load_dish_cfg_{file_name}", command_input_factory
    )

    result_code, message = central_node_mid.load_dish_vcc_configuration(
        load_dish_cfg_json
    )
    pytest.command_result_code = result_code
    pytest.command_result_message = message


@then(parsers.parse("TMC rejects the command with error {error_message}"))
def test_tmc_rejects_command_with_error(error_message):
    """Test validate that command failed with error message"""
    assert pytest.command_result_code == ResultCode.REJECTED
    assert error_message in pytest.command_result_message[0]


@then(
    "TMC rejects the command with error due to Duplicate Vcc ids found in json"
)
def test_tmc_rejects_command_for_duplicate_vcc_id():
    """Test validate that command failed with error message"""
    assert pytest.command_result_code == ResultCode.REJECTED
    assert (
        "Duplicate Vcc ids found in json" in pytest.command_result_message[0]
    )


@when(
    parsers.parse(
        "I issue the command LoadDishCfg on TMC with invalid {dish_id}"
    )
)
def invoke_command_with_invalid_dish_id(
    central_node_mid, command_input_factory, dish_id
):
    """Call load dish cfg command with invalid dish id"""
    # Prepare input for load dish configuration
    load_dish_cfg_json = prepare_json_args_for_centralnode_commands(
        "load_dish_cfg_invalid_dish_id", command_input_factory
    )

    result_code, message = central_node_mid.load_dish_vcc_configuration(
        load_dish_cfg_json
    )
    pytest.command_result_code = result_code
    pytest.command_result_message = message


@when(
    "I issue the command LoadDishCfg on TMC with duplicate "
    "vcc id in configuration"
)
def invoke_command_with_duplicate_vcc_id(
    central_node_mid, command_input_factory
):
    """Call load dish cfg command with invalid duplicate vcc id"""
    # Prepare input for load dish configuration
    load_dish_cfg_json = prepare_json_args_for_centralnode_commands(
        "load_dish_cfg_duplicate_vcc_id", command_input_factory
    )

    result_code, message = central_node_mid.load_dish_vcc_configuration(
        load_dish_cfg_json
    )
    pytest.command_result_code = result_code
    pytest.command_result_message = message


@when(
    "I issue the command LoadDishCfg on TMC "
    "and CSP Controller raises an exception"
)
def invoke_command_load_cfg_on_defective_csp(
    central_node_mid,
    event_recorder,
    command_input_factory,
    simulator_factory,
):
    """Call load_dish_cfg method which invoke LoadDishCfg
    command on CentralNode
    Args:
    :param central_node_mid: fixture for a TMC CentralNode Mid under test
    which provides simulated master devices
    :param event_recorder: fixture for a MockTangoEventCallbackGroup
    for validating the subscribing and receiving events.
    :param simulator_factory: fixture for creating simulator devices for
    mid Telescope respectively.
    :param command_input_factory: fixture for creating input required
    for command
    """
    event_recorder.subscribe_event(
        central_node_mid.central_node, "longRunningCommandResult"
    )
    event_recorder.subscribe_event(
        central_node_mid.csp_master_leaf_node, "longRunningCommandResult"
    )
    # Prepare input for load dish configuration
    load_dish_cfg_json = prepare_json_args_for_centralnode_commands(
        "load_dish_cfg", command_input_factory
    )
    csp_sim = simulator_factory.get_or_create_simulator_device(
        SimulatorDeviceType.MID_CSP_MASTER_DEVICE
    )
    pytest.initial_sysParam = central_node_mid.csp_master_leaf_node.sysParam
    pytest.initial_sourceSysParam = (
        central_node_mid.csp_master_leaf_node.sourceSysParam
    )

    csp_sim.SetDefective(ERROR_PROPAGATION_DEFECT)
    _, unique_id = central_node_mid.load_dish_vcc_configuration(
        load_dish_cfg_json
    )
    csp_master_leaf_node_name = (
        central_node_mid.csp_master_leaf_node.dev_name()
    )
    exception_msg = (
        "Exception occurred on device: Command failed on device "
        + f"{csp_master_leaf_node_name}: Exception occurred, command failed."
    )
    pytest.command_result = event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "longRunningCommandResult",
        (unique_id[0], exception_msg),
        lookahead=5,
    )
    csp_sim.SetDefective(RESET_DEFECT)


@then(
    "sysParam and sourceSysParam attributes "
    "remains unchanged on CSP Master Leaf Node"
)
def check_sys_param_source_sys_param_attributes(central_node_mid):
    """Test validate that sysParam and sourceSysParam attributes
    are not updated after error
    """
    assert (
        pytest.initial_sysParam
        == central_node_mid.csp_master_leaf_node.sysParam
    )
    assert (
        pytest.initial_sourceSysParam
        == central_node_mid.csp_master_leaf_node.sourceSysParam
    )


@then(parsers.parse("command returns with error message {error_message}"))
def check_return_msg(error_message: str):
    """Test validate that command failed with error message"""
    assert error_message in pytest.command_result["attribute_value"][1]
