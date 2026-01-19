"""
BDD tests to verify Dish Leaf Node validation failures
(kValue / GPM) degrade Dish, Subarray, and Telescope health.
"""

import json
import logging
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
from ska_tango_testing.mock.placeholders import Anything
from tango import DeviceProxy

from tests.resources.test_harness.helpers import (
    wait_and_validate_device_attribute_value,
)
from tests.resources.test_support.common_utils.result_code import ResultCode
from tests.resources.test_support.common_utils.tmc_helpers import (
    tear_down_configured_alarms,
)
from tests.resources.test_support.constant import (
    alarm_handler1,
    tmc_dish_leaf_node3,
)

# from ska_tango_testing.integration import TangoEventTracer, log_events
from tests.tmc_csp_new_ITH.conftest import SubarrayTestContextData
from tests.tmc_csp_new_ITH.utils.my_file_json_input import MyFileJSONInput
from tests.tmc_new_ITH.conftest import ASSERTIONS_TIMEOUT

# from tests.tmc_new_ITH.utils.utils import setup_event_subscriptions

LOGGER = logging.getLogger(__name__)


def _setup_event_subscriptions(
    tmc: TMCFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
    event_tracer: TangoEventTracer,
):
    """Subscribe TMC, CSP and SDP devices to track and log obsState events.

    :param tmc: the TMC facade.
    :param csp: the CSP facade.
    :param sdp: the SDP facade.
    :param event_tracer: the event tracer.
    """
    event_tracer.subscribe_event(tmc.subarray_node, "healthState")
    event_tracer.subscribe_event(csp.csp_subarray, "healthState")
    event_tracer.subscribe_event(sdp.sdp_subarray, "healthState")
    event_tracer.subscribe_event(tmc.central_node, "telescopeHealthState")
    event_tracer.subscribe_event(
        tmc.dish_leaf_node_list[2], "kvaluevalidationresult"
    )
    event_tracer.subscribe_event(
        tmc.dish_leaf_node_list[2], "gpmValidationResult"
    )
    event_tracer.subscribe_event(tmc.dish_leaf_node_list[2], "healthState")

    # log_events(
    #     {
    #         tmc.subarray_node: [
    #             "healthState",
    #         ],
    #         csp.csp_subarray: ["healthState"],
    #         sdp.sdp_subarray: [
    #             "healthState",
    #         ],
    #         tmc.central_node: [
    #             "telescopeHealthState",
    #         ],
    #         tmc.dish_leaf_node_list[2]: [
    #             "kvaluevalidationresult",
    #             "gpmValidationResult",
    #             "healthState",
    #         ],
    #     },
    #     event_enum_mapping={
    #         "healthState": HealthState,
    #         "telescopeHealthState": HealthState,
    #         "kvaluevalidationresult": ResultCode,
    #     },
    # )


@pytest.fixture
def preserve_dish_state(
    tmc: TMCFacade, dishes: DishesFacade, event_tracer: TangoEventTracer
):
    """
    Preserve and restore Dish Master and Dish Leaf Node state so
    subsequent tests are not affected.
    """
    dish_ln = tmc.dish_leaf_node_list[2]
    dish_master = dishes.dish_master_dict["dish_063"]

    # Preserve original values
    original_kvalue_dln = dish_ln.kValue
    original_kvalue_master = dish_master.kValue
    original_band3_params = list(dish_master.band3PointingModelParams)

    yield

    # Restore kValue
    dish_ln.SetKValue(original_kvalue_dln)
    dish_master.SetKValue(original_kvalue_master)

    # Restore Band-2 pointing model params (GPM driver)
    dish_master.band3PointingModelParams = original_band3_params

    # Allow validation to settle
    time.sleep(2)

    # Assertions after reset
    # assert int(dish_ln.kValueValidationResult) == ResultCode.OK.value
    assert int(dish_ln.kvaluevalidationresult) == ResultCode.OK.value

    # gpm_result = json.loads(dish_ln.gpmValidationResult)
    # assert all(value == "OK" for value in gpm_result.values())

    gpm_result = json.loads(dish_ln.gpmValidationResult)
    assert gpm_result.get("Band_3") == "OK"

    # assert_that(event_tracer).described_as(
    #     "Dish Leaf Node kValueValidationResult should change to Ok"
    # ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
    #     dish_ln,
    #     "kValueValidationResult",
    #     ResultCode.OK,
    # )

    # # Wait for a GPM validation change event
    # event = (
    #     assert_that(event_tracer)
    #     .described_as("DLN gpmValidationResult should report Band_3 OK")
    #     .within_timeout(ASSERTIONS_TIMEOUT)
    #     .has_change_event_occurred(
    #         dish_ln,
    #         "gpmValidationResult",
    #         Anything,
    #         lookahead=3,
    #     )
    # )

    # # Validate the event payload
    # gpm_result = json.loads(event["attribute_value"])
    # assert_that(gpm_result.get("Band_3")).is_equal_to("OK")

    assert tmc.central_node.IsDishVccConfigSet is True


@pytest.mark.batchval1
@pytest.mark.SKA_mid
@scenario(
    "../tmc_new_ITH/features/xtp_97749_dish_validation_health.feature",
    "Dish validation failure impacts telescope health",
)
def test_dish_validation_impacts_health():
    """BDD Scenario Outline test"""


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

    _setup_event_subscriptions(tmc, csp, sdp, event_tracer)

    csp.csp_subarray.SetDirectHealthState(HealthState.OK)
    sdp.sdp_subarray.SetDirectHealthState(HealthState.OK)

    # event_tracer.subscribe_event(tmc.subarray_node, "healthState")
    # event_tracer.subscribe_event(csp.csp_subarray, "healthState")
    # event_tracer.subscribe_event(sdp.sdp_subarray, "healthState")
    # event_tracer.subscribe_event(tmc.central_node, "telescopeHealthState")

    # csp.csp_subarray.SetDirectHealthState(HealthState.OK)
    # sdp.sdp_subarray.SetDirectHealthState(HealthState.OK)


@given("Telescope is in ON state")
def telescope_in_on_state(tmc: TMCFacade):
    """
    Ensure that the telescope is transitioned to the ON state.

    :param tmc: TMC facade used to control telescope state.
    """
    tmc.move_to_on(wait_termination=True, is_long_running_command=True)


@given("I assign resources to TMC Subarray")
def invoke_assign_resources(
    context_fixt: SubarrayTestContextData, tmc: TMCFacade
):
    """Invoke Assign Resources"""
    json_input = MyFileJSONInput(
        "centralnode", "assign_resources_mid"
    ).with_attribute("subarray_id", 1)

    context_fixt.when_action_result = tmc.assign_resources(
        json_input,
        wait_termination=True,
    )


@given(
    parsers.parse(
        'Dish Leaf Node has "{validation_type}" validation condition'
    )
)
def prepare_validation_condition(
    tmc: TMCFacade,
    dishes: DishesFacade,
    validation_type: str,
    event_tracer: TangoEventTracer,
    preserve_dish_state,
):
    """
    Prepare Dish Leaf Node validation condition and
    assert validation results immediately after setting.
    """
    dish_ln = tmc.dish_leaf_node_list[2]
    dish_master = dishes.dish_master_dict["dish_063"]

    LOGGER.info("In prepare_validation_condition")

    # REQUIRED SUBSCRIPTIONS

    # event_tracer.subscribe_event(dish_ln, "kValueValidationResult")
    # event_tracer.subscribe_event(dish_ln, "kvaluevalidationresult")
    # event_tracer.subscribe_event(dish_ln, "gpmValidationResult")
    # event_tracer.subscribe_event(dish_ln, "healthState")
    # event_tracer.subscribe_event(tmc.subarray_node, "healthState")
    # event_tracer.subscribe_event(csp.csp_subarray, "obsState")
    # event_tracer.subscribe_event(sdp.sdp_subarray, "obsState")
    # event_tracer.subscribe_event(tmc.central_node, "telescopeHealthState")

    # Allow event_tracer to settle
    # time.sleep(2)

    if validation_type == "all_ok":
        # assert int(dish_ln.kValueValidationResult) == ResultCode.OK.value
        assert int(dish_ln.kvaluevalidationresult) == ResultCode.OK.value
        gpm_result = json.loads(dish_ln.gpmValidationResult)
        # assert all(value == "OK" for value in gpm_result.values())
        assert any(value != "FAILED" for value in gpm_result.values())
        LOGGER.info("prepare_validation_condition-DLN GPM validation result:")
        for band, value in gpm_result.items():
            LOGGER.info("  %s: %s", band, value)

    elif validation_type == "kvalue mismatch":
        LOGGER.info("In prepare_validation_condition kvalue mismatch")

        dish_ln.SetKValue(1)
        dish_master.SetKValue(2)

        # assert int(dish_ln.kValueValidationResult) == ResultCode.FAILED.value
        # assert_that(event_tracer).has_change_event_occurred(
        #     dish_ln,
        #     "kValueValidationResult",
        #     ResultCode.FAILED.value,
        # )

        assert wait_and_validate_device_attribute_value(
            dish_ln,
            "kvaluevalidationresult",
            str(ResultCode.FAILED.value),
            # ResultCode.FAILED.value,
        )

        assert_that(event_tracer).described_as(
            "Dish Leaf Node kValueValidationResult should change to FAILED"
        ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
            dish_ln,
            # "kValueValidationResult",
            "kvaluevalidationresult",
            str(ResultCode.FAILED.value),
            # ResultCode.FAILED.value,
        )

    elif validation_type == "gpm mismatch":

        LOGGER.info("In prepare_validation_condition gpm mismatch")

        # Keep kValue consistent
        dish_ln.SetKValue(1)
        dish_master.SetKValue(1)

        assert wait_and_validate_device_attribute_value(
            dish_ln,
            "kvaluevalidationresult",
            # ResultCode.OK.value,
            str(ResultCode.OK.value),
        )

        assert_that(event_tracer).described_as(
            "Dish Leaf Node kValueValidationResult should change to Ok"
        ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
            dish_ln,
            # "kValueValidationResult",
            "kvaluevalidationresult",
            # ResultCode.OK.value,
            str(ResultCode.OK.value),
        )

        # Introduce GPM mismatch via Dish Master Band-3 params
        invalid_params = [0.0] * 18
        invalid_params[0] = 999.0
        dish_master.band3PointingModelParams = invalid_params

        # Wait for a GPM validation change event

        assert_that(event_tracer).described_as(
            "DLN gpmValidationResult should report Band_3 FAILED"
        ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
            dish_ln,
            "gpmValidationResult",
            Anything,
        )

        # Validate the event payload
        gpm_result = json.loads(dish_ln.gpmValidationResult)
        assert_that(gpm_result.get("Band_3")).is_equal_to("FAILED")

    else:
        raise ValueError(f"Unsupported validation_type: {validation_type}")


@when("Dish Leaf Node health is evaluated")
def evaluate_health(tmc: TMCFacade):
    """
    Health evaluation is triggered implicitly by validation callbacks.
    :param tmc: TMC facade
    """
    LOGGER.info("In evaluate_health")
    pass


@then(parsers.parse('Dish Leaf Node healthState shall be "{dln_health}"'))
def verify_dln_health(
    tmc: TMCFacade,
    event_tracer: TangoEventTracer,
    dln_health: str,
):
    """
    Verify the Dish Leaf Node health state.

    This step asserts that a Tango change event for the Dish
    Leaf Node healthState matches the expected value.

    :param tmc: TMC facade providing access to the Dish Leaf Node.
    :param event_tracer: Utility used to capture and assert change events.
    :param expected_health: Expected Dish Leaf Node health state.
    """
    dish_ln = tmc.dish_leaf_node_list[2]

    LOGGER.info("In verify_dln_health")

    # instead of waiting for an event
    # assert dish_ln.healthState == HealthState.OK
    # assert dish_ln.healthState == HealthState[expected_health]

    assert_that(event_tracer).described_as(
        "Dish Leaf Node healthState should change " f"to {dln_health}"
    ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
        dish_ln,
        "healthState",
        HealthState[dln_health],
    )


@then(
    parsers.parse(
        'TMC Subarray Node healthState shall be "{propagated_health}"'
    )
)
def verify_subarray_health(
    tmc: TMCFacade,
    event_tracer: TangoEventTracer,
    propagated_health: str,
):
    """
    Verify the TMC Subarray Node health state.

    This step confirms that healthstate change
    propagates from the Dish Leaf Node to the Subarray Node.

    :param tmc: TMC facade providing access to the Subarray Node.
    :param event_tracer: Utility used to capture and assert change events.
    :param expected_health: Expected Subarray health state.
    """

    LOGGER.info("In verify_subarray_health")

    # instead of waiting for an event
    # assert tmc.subarray_node.healthState == HealthState[expected_health]

    assert_that(event_tracer).described_as(
        "TMC Subarray Node healthState should change "
        f"to {propagated_health}"
    ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
        tmc.subarray_node,
        "healthState",
        HealthState[propagated_health],
    )


@then(parsers.parse('telescopeHealthState shall be "{propagated_health}"'))
def verify_telescope_health(
    tmc: TMCFacade,
    event_tracer: TangoEventTracer,
    propagated_health: str,
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
    LOGGER.info("In verify_telescope_health")

    assert_that(event_tracer).described_as(
        "Telescope healthState should change " f"to {propagated_health}"
    ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
        tmc.central_node,
        "telescopeHealthState",
        HealthState[propagated_health],
    )


@then(
    parsers.parse(
        'an alarm shall be raised for "{validation_type}" validation failure'
    )
)
def verify_alarm_raised(validation_type):
    """
    Verify the corresponding alarm is raised
    on the Alarm Handler.
    """
    LOGGER.info("In verify_alarm_raised")

    alarm_handler = DeviceProxy(alarm_handler1)

    if validation_type == "all_ok":
        return  # No alarm expected

    if validation_type == "kvalue mismatch":
        expected_tag = "DishLeafNode_kValue_mismatch"
        alarm_formula = (
            f"tag={expected_tag};"
            # f"formula=({tmc_dish_leaf_node3}/kValueValidationResult!= 'OK');"
            f"formula=({tmc_dish_leaf_node3}/kvaluevalidationresult != 'OK');"
            "priority=log;"
            "group=none;"
            'message="Alarm raised when Dish Leaf Node detects '
            'kValue mismatch with Dish Manager"'
        )

        alarm_handler.Load(alarm_formula)
        alarm_list = alarm_handler.alarmList
        assert alarm_list == ("dishleafnode_kvalue_mismatch",)
        tear_down_configured_alarms(alarm_handler, alarm_list)

    # elif validation_type == "gpm mismatch":
    #     expected_tag = "DishLeafNode_GPM_mismatch"
    #     alarm_formula = (
    #         f"tag={expected_tag};"
    #         f"formula=({tmc_dish_leaf_node3}/gpmValidationResult "
    #         "CONTAINS 'FAILED');"
    #         "priority=log;"
    #         "group=none;"
    #         'message="Alarm raised when Dish Leaf Node detects '
    #         'GPM validation failure for one or more bands"'
    #     )

    #     alarm_handler.Load(alarm_formula)
    #     alarm_list = alarm_handler.alarmList
    #     assert alarm_list == ("dishleafnode_gpm_mismatch",)
    #     tear_down_configured_alarms(alarm_handler, alarm_list)

    else:
        raise ValueError(validation_type)

    # alarm_handler.Load(alarm_formula)
    # alarm_list = alarm_handler.alarmList
    # assert alarm_list == ("dishleafnode_kvalue_mismatch",)
    # tear_down_configured_alarms(alarm_handler, alarm_list)

    # # Load alarm
    # alarm_handler.Load(alarm_formula)
    # alarm_list = alarm_handler.alarmList

    # assert expected_tag in alarm_list

    # # Allow alarm to propagate
    # time.sleep(3)

    # alarm_summary = alarm_handler.alarmSummary
    # assert any(expected_tag in alarm for alarm in alarm_summary)

    # # Cleanup
    # tear_down_configured_alarms(alarm_handler, alarm_list)
