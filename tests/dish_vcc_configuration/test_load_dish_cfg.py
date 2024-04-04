import json

import pytest
from pytest_bdd import given, scenario, then, when
from tango import DevState

from tests.resources.test_harness.helpers import (
    device_attribute_changed,
    get_master_device_simulators,
    prepare_json_args_for_centralnode_commands,
)
from tests.resources.test_support.common_utils.result_code import ResultCode


@pytest.mark.skip(
    reason="Test fails because of TRANSIENT CORBA EXCEPTION with command"
    + " exceeding the timeout of 3 seconds"
)
@pytest.mark.SKA_mid
@scenario(
    "../features/load_dish_cfg_command.feature",
    "TMC is able to load Dish and VCC configuration file",
)
def test_dish_id_vcc_configuration():
    """This test validate that TMC is able to load the dish vcc
    configuration file provided to LoadDishCfg command.
    Validate that k-numbers set on dish masters
    Validate sysParam and sourceSysParam attribute set on csp master leaf node
    """


@given("a TMC")
def given_tmc():
    """Given a TMC"""


@given("Telescope is in ON state")
def telescope_in_on_state(central_node_mid, event_recorder):
    """Move Telescope to ON state
    Args
    :param central_node_mid: fixture for a TMC CentralNode Mid under test
    which provides simulated master devices
    :param event_recorder: fixture for a MockTangoEventCallbackGroup
    for validating the subscribing and receiving events.
    """
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
    "I issue the command LoadDishCfg on TMC with Dish and VCC "
    "configuration file"
)
def invoke_load_dish_cfg(
    central_node_mid, event_recorder, command_input_factory
):
    """Call load_dish_cfg method which invoke LoadDishCfg
    command on CentralNode
    Args:
    :param central_node_mid: fixture for a TMC CentralNode Mid under test
    which provides simulated master devices
    :param event_recorder: fixture for a MockTangoEventCallbackGroup
    for validating the subscribing and receiving events.
    :param command_input_factory: fixture for creating input required
    for command
    """
    # Subscribe for longRunningCommandResult attribute
    event_recorder.subscribe_event(
        central_node_mid.central_node, "longRunningCommandResult"
    )
    # Prepare input for load dish configuration
    load_dish_cfg_json = prepare_json_args_for_centralnode_commands(
        "load_dish_cfg", command_input_factory
    )

    _, unique_id = central_node_mid.load_dish_vcc_configuration(
        load_dish_cfg_json
    )

    assert event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "longRunningCommandResult",
        (unique_id[0], str(int(ResultCode.OK))),
        lookahead=5,
    )


@then("TMC should pass the configuration to CSP Controller")
def tmc_pass_configuration_to_csp_controller(simulator_factory):
    """Validate sysParam and sourceSysParam attribute set on Csp Master
    :param simulator_factory: fixture for creating simulator devices for
    mid Telescope respectively.
    """
    csp_master_sim, _, _, _, _ = get_master_device_simulators(
        simulator_factory
    )
    expected_sys_param = {
        "interface": "https://schema.skao.int"
        "/ska-mid-cbf-initial-parameters/2.2",
        "dish_parameters": {
            "SKA001": {"vcc": 1, "k": 11},
            "SKA036": {"vcc": 2, "k": 101},
        },
    }
    assert json.loads(csp_master_sim.sysParam) == expected_sys_param


@then("TMC displays the current version of Dish and VCC configuration")
def validate_sys_param_attribute_set(central_node_mid):
    """Valdate sysParam and sourceSysParam attribute
    correctly set on csp master leaf node
    :param central_node_mid: fixture for a TMC CentralNode Mid under test
    which provides simulated master devices
    """
    interface_schema = (
        "https://schema.skao.int/ska-mid-cbf-initial-parameters/2.2"
    )
    expected_sys_param = json.dumps(
        {
            "interface": interface_schema,
            "dish_parameters": {
                "SKA001": {"vcc": 1, "k": 11},
                "SKA036": {"vcc": 2, "k": 101},
            },
        }
    )
    expected_source_sys_param = json.dumps(
        {
            "interface": interface_schema,
            "tm_data_sources": [
                "gitlab://gitlab.com/ska-telescope/ska-telmodel-data?main#"
                + "tmdata"
            ],
            "tm_data_filepath": (
                "instrument/dishid_vcc_configuration/mid_cbf_parameters.json"
            ),
        }
    )

    assert device_attribute_changed(
        device=central_node_mid.csp_master_leaf_node,
        attribute_name_list=["sysParam", "sourceSysParam"],
        attribute_value_list=[expected_sys_param, expected_source_sys_param],
        timeout=100,
    ), (
        "sysParam and sourceSysParam attribute value is not set "
        "on csp master leaf node"
    )


@then("TMC should set Dish k-numbers provided in file on dish master devices")
def validate_k_number_set(simulator_factory):
    """Validate k-numbers set on dish masters
    :param simulator_factory: fixture for creating simulator devices for
    mid Telescope respectively.
    """
    (
        _,
        _,
        dish_master_1_sim,
        dish_master_2_sim,
        _,
    ) = get_master_device_simulators(simulator_factory)
    assert dish_master_1_sim.kValue == 11
    assert dish_master_2_sim.kValue == 101
