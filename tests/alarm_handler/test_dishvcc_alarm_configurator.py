"""Test module for TMC-DISH On functionality"""

import json
import time

import pytest
from pytest_bdd import given, scenario, then, when
from tango import DeviceProxy, DevState

from tests.resources.test_harness.helpers import (
    wait_and_validate_device_attribute_value,
)
from tests.resources.test_support.common_utils.result_code import ResultCode
from tests.resources.test_support.common_utils.tmc_helpers import (
    tear_down_configured_alarms,
)
from tests.resources.test_support.constant import alarm_handler1


@pytest.mark.SKA_mid
@scenario(
    "../features/dish_vcc_initialization/" "xtp_alarm_dish_vcc.feature",
    "TMC validates and raises alarm when K-Value not set in Dish Leaf Nodes",
)
def test_tmc_validate_dln_kvalue_not_set():
    """
    Test case to verify Dish-VCC validation functionality

    Glossary:
        - "event_recorder": fixture for EventRecorder class
        - "tmc_mid": fixture to give TMC mid device server commands
    """


@given("a TMC with already loaded Dish-VCC map version")
def given_tmc_with_already_loaded_dish_vcc_config_version(tmc_mid):
    """Given a TMC with loaded Dish-VCC map version"""
    cspmln_validation_string = "TMC and CSP Master Dish Vcc Version is Same"
    central_node_dish_vcc_validation_status = {
        "dish": "ALL DISH OK",
        "ska_mid/tm_leaf_node/csp_master": cspmln_validation_string,
    }
    assert (
        json.loads(tmc_mid.DishVccValidationStatus)
        == central_node_dish_vcc_validation_status
    )
    assert tmc_mid.IsDishVccConfigSet


@when("the Dish Leaf Node is restarted")
def restart_the_dish_leaf_nodes(tmc_mid):
    """Restart the dish leaf nodes"""
    # Unset values on some of the Dish Leaf Nodes

    tmc_mid.central_node.dish_leaf_node_list[0].kValue = 0

    # [0, 1, 2, 3] are index for dish leaf node list
    tmc_mid.RestartServer("DISHLN_0")


@when("the Dish Leaf Node finds k-value not set on Dish Leaf Node")
def check_dishln_is_on_and_kvalue_validation_accomplished(tmc_mid):
    """Method to check dish leaf node are up and
    k-value validation is completed"""
    assert wait_and_validate_device_attribute_value(
        tmc_mid.central_node.dish_leaf_node_list[0], "State", DevState.ON
    )
    assert wait_and_validate_device_attribute_value(
        tmc_mid.central_node.dish_leaf_node_list[0],
        "kValueValidationResult",
        str(int(ResultCode.UNKNOWN)),
    )


@then("the alarm is raised for kValue not set")
def test_load_alarm():
    """A method to load tmc alarm for Alarm handler instance"""
    global alarm_handler, alarm_list
    alarm_handler = DeviceProxy(alarm_handler1)
    alarm_formula = (
        "tag=dishleafnode_kvalue_not_set;formula="
        "(ska_mid/tm_leaf_node/d0001/kValueValidationResult == '4' );"
        "priority=log;group=none;message="
        "alarm for dishvalidation status raised when k-value is not set"
    )
    alarm_handler.Load(alarm_formula)
    alarm_list = alarm_handler.alarmList
    assert ("dishleafnode_kvalue_not_set") in alarm_list
    time.sleep(3)
    alarm_summary = alarm_handler.alarmSummary
    assert "UNACK" in alarm_summary[0]
    # tear_down_configured_alarms(alarm_handler, alarm_list)


@then(
    "the Central Node reports the same and prohibits "
    + "any further command execution"
)
def check_value_of_isdishvccconfigset_on_central_node(tmc_mid):
    """Method to verify isDishVccConfig attribute is true
    or false after dish leaf node report."""
    cspmln_validation_string = "TMC and CSP Master Dish Vcc Version is Same"
    central_node_dish_vcc_validation_status = {
        "d0001": "k-value not set",
        "ska_mid/tm_leaf_node/csp_master": cspmln_validation_string,
    }
    assert wait_and_validate_device_attribute_value(
        tmc_mid.central_node.central_node,
        "DishVccValidationStatus",
        json.dumps(central_node_dish_vcc_validation_status),
        is_json=True,
    )
    assert not tmc_mid.IsDishVccConfigSet
    # Central Node does not allow any command execution
    with pytest.raises(Exception) as e:
        tmc_mid.TelescopeOn()
    assert "Dish Vcc Config not Set" in str(e.value)
    # Restore to previous k-value
    tmc_mid.central_node.dish_leaf_node_list[0].SetKValue(111)
    tear_down_configured_alarms(alarm_handler, alarm_list)
    assert wait_and_validate_device_attribute_value(
        tmc_mid.central_node.central_node,
        "isDishVccConfigSet",
        True,
    )
