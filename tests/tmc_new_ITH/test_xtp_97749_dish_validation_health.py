"""
BDD tests to verify Dish Leaf Node validation failures
(kValue / GPM) degrade Dish, Subarray, and Telescope health.
"""

import time

import pytest
from assertpy import assert_that
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import HealthState
from ska_integration_test_harness.facades.csp_facade import CSPFacade
from ska_integration_test_harness.facades.dishes_facade import DishesFacade
from ska_integration_test_harness.facades.sdp_facade import SDPFacade
from ska_integration_test_harness.facades.tmc_facade import TMCFacade
from ska_tango_testing.integration import TangoEventTracer
from tango import DeviceProxy

from tests.resources.test_support.common_utils.result_code import ResultCode
from tests.resources.test_support.common_utils.tmc_helpers import (
    tear_down_configured_alarms,
)
from tests.resources.test_support.constant import alarm_handler1
from tests.tmc_new_ITH.conftest import ASSERTIONS_TIMEOUT
from tests.tmc_new_ITH.utils.utils import setup_event_subscriptions


@pytest.mark.batchval1
@pytest.mark.SKA_mid
@scenario(
    "../tmc_new_ITH/features/xtp_97749_dish_validation_health.feature",
    "Dish validation failure impacts telescope health",
)
def test_dish_validation_impacts_health():
    """BDD Scenario Outline test"""


@pytest.fixture
def preserve_dish_state(tmc: TMCFacade, dish_master: DishesFacade):
    """
    Preserve and restore Dish Leaf Node validation state so
    subsequent tests are not affected.
    """
    dish_ln = tmc.dish_leaf_node_list[0]
    dish_Master = dish_master.dish_master_list[3]

    # Preserve original values
    original_kvalue_dln = dish_ln.kValue
    original_kvalue_master = dish_Master.kValue
    original_gpm_results = dict(dish_ln.gpmValidationResult)
    # original_gpm_results = dict(
    #     dish_ln.component_manager._gpm_validation_result
    # )

    yield

    #  Restore kValue
    dish_ln.SetKValue(original_kvalue_dln)
    dish_Master.SetKValue(original_kvalue_master)
    # dish_ln.component_manager._dish_manager_kvalue = str(original_kvalue)
    dish_ln.kvalue_validation_callback()

    # Restore GPM
    for band, result in original_gpm_results.items():
        dish_ln.update_gpm_validation_result_callback(band, result)

    #  Assertions after reset
    assert dish_ln.kValueValidationResult == ResultCode.OK

    for result in dish_ln.gpmValidationResult.values():
        assert result == "OK"

    assert tmc.central_node.IsDishVccConfigSet is True


@given("a TMC")
def given_a_tmc(
    tmc: TMCFacade,
    sdp: SDPFacade,
    csp: CSPFacade,
    event_tracer: TangoEventTracer,
):
    """
    Given a TMC
    :param tmc: TMC facade providing access to Central, Subarray,
            and Dish Leaf Node components.
    :param event_tracer: Utility used to trace and assert Tango events.
    """

    setup_event_subscriptions(tmc, csp, sdp, event_tracer)


@given("Telescope is in ON state")
def telescope_in_on_state(tmc: TMCFacade):
    """
    Ensure that the telescope is transitioned to the ON state.

    :param tmc: TMC facade used to control telescope state.
    """
    tmc.move_to_on()


@given(
    parsers.parse(
        'Dish Leaf Node has "{validation_type}" validation condition'
    )
)
def prepare_validation_condition(
    tmc: TMCFacade,
    dish_master: DishesFacade,
    validation_type: str,
    preserve_dish_state,
):
    """
    Prepare Dish Leaf Node validation condition and
    assert validation results immediately after setting.
    """
    dish_ln = tmc.dish_leaf_node_list[0]
    # dish_Master = tmc.dish_master_list[3]
    dish_Master = dish_master.dish_master_list[3]

    if validation_type == "all_ok":
        dish_ln.kvalue_validation_callback()
        dish_ln.update_gpm_validation_result_callback("band2", "OK")

        assert dish_ln.kValueValidationResult == ResultCode.OK
        assert dish_ln.gpmValidationResult["band2"] == "OK"
        # assert (
        #     dish_ln.component_manager._gpm_validation_result["band2"] == "OK"
        # )

    elif validation_type == "gpm mismatch":
        dish_ln.kvalue_validation_callback()
        dish_ln.update_gpm_validation_result_callback("band2", "FAILED")

        assert dish_ln.kValueValidationResult == ResultCode.OK
        assert dish_ln.gpmValidationResult["band2"] == "FAILED"
        # assert (
        #     dish_ln.component_manager._gpm_validation_result["band2"]
        #     == "FAILED"
        # )

    elif validation_type == "kvalue mismatch":
        dish_ln.SetKValue(1)
        dish_Master.SetKValue(2)
        # dish_ln.component_manager._dish_manager_kvalue = "2"
        dish_ln.kvalue_validation_callback()

        assert dish_ln.kValueValidationResult == ResultCode.FAILED

    else:
        raise ValueError(f"Unsupported validation_type: {validation_type}")


@when("Dish Leaf Node health is evaluated")
def evaluate_health(tmc: TMCFacade):
    """
    Health evaluation is triggered implicitly by validation callbacks.
    :param tmc: TMC facade
    """
    pass


@then(parsers.parse('Dish Leaf Node healthState shall be "{expected_health}"'))
def verify_dln_health(
    tmc: TMCFacade,
    event_tracer: TangoEventTracer,
    expected_health: str,
):
    """
    Verify the Dish Leaf Node health state.

    This step asserts that a Tango change event for the Dish
    Leaf Node healthState matches the expected value.

    :param tmc: TMC facade providing access to the Dish Leaf Node.
    :param event_tracer: Utility used to capture and assert change events.
    :param expected_health: Expected Dish Leaf Node health state.
    """
    dish_ln = tmc.dish_leaf_node_list[0]

    assert_that(event_tracer).within_timeout(
        ASSERTIONS_TIMEOUT
    ).has_change_event_occurred(
        dish_ln,
        "healthState",
        HealthState[expected_health],
    )


# @then(
#  parsers.parse('TMC Subarray Node healthState shall be "{expected_health}"')
# )
# def verify_subarray_health(
#     tmc: TMCFacade,
#     event_tracer: TangoEventTracer,
#     expected_health: str,
# ):
#     """
#     Verify the TMC Subarray Node health state.

#     This step confirms that healthstate change
#     propagates from the Dish Leaf Node to the Subarray Node.

#     :param tmc: TMC facade providing access to the Subarray Node.
#     :param event_tracer: Utility used to capture and assert change events.
#     :param expected_health: Expected Subarray health state.
#     """
#     assert_that(event_tracer).within_timeout(
#         ASSERTIONS_TIMEOUT
#     ).has_change_event_occurred(
#         tmc.subarray_node,
#         "healthState",
#         HealthState[expected_health],
#     )


@then(parsers.parse('telescopeHealthState shall be "{expected_health}"'))
def verify_telescope_health(
    tmc: TMCFacade,
    event_tracer: TangoEventTracer,
    expected_health: str,
):
    """
    Verify the overall telescope health state.

    This step ensures that Dish-level validation failures
    propagate through the system hierarchy up to the
    Telescope (Central Node) health state.

    :param tmc: TMC facade providing access to the Central Node.
    :param event_tracer: Utility used to capture and assert change events.
    :param expected_health: Expected telescope health state.
    """
    assert_that(event_tracer).within_timeout(
        ASSERTIONS_TIMEOUT
    ).has_change_event_occurred(
        tmc.central_node,
        "telescopeHealthState",
        HealthState[expected_health],
    )


@then(
    parsers.parse(
        'an alarm shall be raised for "{validation_type}" validation failure'
    )
)
def verify_alarm_raised(validation_type):
    """
    Verify that the correct alarm is raised based on validation failure
    using rules loaded from alarm rules file.
    """
    alarm_handler = DeviceProxy(alarm_handler1)

    # Load alarm rules from file
    alarm_handler.LoadFromFile(
        "tests/data/alarm_rules/dish_leaf_node_validation_alarms.txt"
    )

    if validation_type == "all_ok":
        # No alarm expected
        time.sleep(2)
        assert alarm_handler.alarmSummary == []
        return

    if validation_type == "kvalue mismatch":
        expected_tag = "DishLeafNode_kValue_mismatch"

    elif validation_type == "gpm mismatch":
        expected_tag = "DishLeafNode_GPM_mismatch"

    else:
        raise ValueError(f"Unsupported validation_type: {validation_type}")

    # Allow alarm engine to evaluate rules
    time.sleep(3)

    alarm_list = alarm_handler.alarmList
    assert expected_tag in alarm_list

    alarm_summary = alarm_handler.alarmSummary
    assert any(expected_tag in alarm for alarm in alarm_summary)

    # Cleanup alarms so other tests are not affected
    tear_down_configured_alarms(alarm_handler, alarm_list)


# @then(
#     parsers.parse(
#         'an alarm shall be raised for "{validation_type}" validation failure'
#     )
# )
# def verify_alarm_raised(validation_type):
#     """
#     Verify the corresponding alarm is raised
#     on the Alarm Handler.
#     """
#     alarm_handler = DeviceProxy(alarm_handler1)

#     if validation_type == "all_ok":
#         return  # No alarm expected

#     if validation_type == "kvalue":
#         alarm_formula = (
#             "tag=DishLeafNode_kValue_mismatch;"
#             f"formula=({tmc_dish_leaf_node1}/kValueValidationResult == '2');"
#             "priority=log;group=none;"
#             'message="alarm raised for kValue mismatch on Dish Leaf Node"'
#         )
#         expected_tag = "DishLeafNode_kValue_mismatch"

#     elif validation_type == "gpm":
#         "tag=DishLeafNode_GPM_mismatch;"
#         alarm_formula = (
#             "formula=("
#             f"{tmc_dish_leaf_node1}/gpmValidationResult == "
#             f"{ResultCode.FAILED}"
#             ");"
#         )

#         expected_tag = "DishLeafNode_GPM_mismatch"

#     else:
#         raise ValueError(validation_type)

#     # Load alarm
#     alarm_handler.Load(alarm_formula)
#     alarm_list = alarm_handler.alarmList

#     assert expected_tag in alarm_list

#     # Allow alarm to propagate
#     time.sleep(3)

#     alarm_summary = alarm_handler.alarmSummary
#     assert any(expected_tag in alarm for alarm in alarm_summary)

#     # Cleanup
#     tear_down_configured_alarms(alarm_handler, alarm_list)
