"""Test auto stow functionality on DishLeafNode."""
# import json
# from os.path import dirname, join

import pytest

# import tango
from assertpy import assert_that
from pytest_bdd import given, scenario, then, when
from ska_integration_test_harness.facades import DishesFacade
from ska_integration_test_harness.facades.tmc_facade import TMCFacade
from ska_tango_testing.integration import TangoEventTracer

from tests.conftest import LOGGER

# from tests.resources.test_harness.utils.enums import StowStatus
from tests.resources.test_support.common_utils.result_code import ResultCode
from tests.resources.test_support.constant import COMMAND_COMPLETED
from tests.resources.test_support.enum import DishMode

# from tests.tmc_new_ITH.weather_sim import (
#     simulate_temperature,
#     simulate_windspeed,
# )

ASSERTIONS_TIMEOUT = 60


def _setup_event_subscriptions(
    tmc: TMCFacade,
    event_tracer: TangoEventTracer,
):
    """Subscribe TMC and Dishes devices to track and log stowStatus events.

    :param tmc: the TMC facade.
    :param dishes: the Dishes facade.
    :param event_tracer: the event tracer.
    """
    dish_leaf_node = tmc.dish_leaf_node_list[0]
    event_tracer.subscribe_event(dish_leaf_node, "stowStatus")
    event_tracer.subscribe_event(dish_leaf_node, "dishMode")
    event_tracer.subscribe_event(dish_leaf_node, "longRunningCommandResult")


@pytest.mark.aki2
@pytest.mark.SKA_mid
@scenario(
    "../tmc_new_ITH/features/auto_stow.feature",
    "TMC validates SetStowMode command on DishLeafNode",
)
def test_verify_setstowmode(tmc: TMCFacade, event_tracer: TangoEventTracer):
    """Test AssignResources with SDP v1.0."""
    _setup_event_subscriptions(tmc, event_tracer)


@given("a DishLeafNode device in STANDBY_LP mode")
def given_tmc_and_dishes(
    tmc: TMCFacade, dishes: DishesFacade, event_tracer: TangoEventTracer
):
    """Given TMC and Dishes facades."""
    LOGGER.info("Testing SetStowMode command on DishLeafNode")
    dish_leaf_node = tmc.dish_leaf_node_list[0]
    dishes.dish_master_dict["dish_001"].SetDirectDishMode(DishMode.STANDBY_FP)
    event_tracer.subscribe_event(dish_leaf_node, "dishMode")
    event_tracer.subscribe_event(dish_leaf_node, "longRunningCommandResult")

    assert_that(event_tracer).within_timeout(
        ASSERTIONS_TIMEOUT
    ).has_change_event_occurred(
        dish_leaf_node, "dishMode", DishMode.STANDBY_FP
    )

    result, unique_id = dish_leaf_node.SetStandbyLPMode()
    assert result[0] == ResultCode.QUEUED

    assert_that(event_tracer).within_timeout(
        ASSERTIONS_TIMEOUT
    ).has_change_event_occurred(
        dish_leaf_node, "dishMode", DishMode.STANDBY_LP
    )
    assert_that(event_tracer).within_timeout(
        ASSERTIONS_TIMEOUT
    ).has_change_event_occurred(
        dish_leaf_node,
        "longRunningCommandResult",
        (unique_id[0], COMMAND_COMPLETED),
    )


@when("I invoke the SetStowMode command on the DishLeafNode")
def when_invoke_setstowmode(tmc: TMCFacade):
    """When I invoke the SetStowMode command on the DishLeafNode."""
    dish_leaf_node = tmc.dish_leaf_node_list[0]
    _, pytest.unique_id = dish_leaf_node.SetStowMode()


@then("the dish transitions to STOW mode")
def then_dish_transitions_to_stow_mode(
    tmc: TMCFacade, event_tracer: TangoEventTracer
):
    """Then the dish transitions to STOW mode."""
    dish_leaf_node = tmc.dish_leaf_node_list[0]

    assert_that(event_tracer).within_timeout(
        ASSERTIONS_TIMEOUT
    ).has_change_event_occurred(dish_leaf_node, "dishMode", DishMode.STOW)


@then("the longRunningCommandResult event confirms command completion")
def then_long_running_command_completes(
    tmc: TMCFacade, event_tracer: TangoEventTracer
):
    """Then the longRunningCommandResult event confirms command completion."""
    dish_leaf_node = tmc.dish_leaf_node_list[0]
    assert_that(event_tracer).within_timeout(
        ASSERTIONS_TIMEOUT
    ).has_change_event_occurred(
        dish_leaf_node,
        "longRunningCommandResult",
        (pytest.unique_id[0], COMMAND_COMPLETED),
    )
