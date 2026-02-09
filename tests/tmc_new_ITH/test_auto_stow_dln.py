"""Tests for automatic stowing functionality on DishLeafNode devices."""
import json
from os.path import dirname, join

import pytest
import tango
from assertpy import assert_that
from ska_integration_test_harness.facades import DishesFacade
from ska_integration_test_harness.facades.tmc_facade import TMCFacade
from ska_tango_testing.integration import TangoEventTracer

from tests.conftest import LOGGER, get_input_str
from tests.resources.test_harness.utils.enums import StowStatus
from tests.resources.test_support.common_utils.result_code import ResultCode
from tests.resources.test_support.constant import COMMAND_COMPLETED
from tests.resources.test_support.enum import DishMode
from tests.tmc_new_ITH.weather_sim import (
    simulate_temperature,
    simulate_windspeed,
)

# pylint: disable=E501
ASSERTIONS_TIMEOUT = 60


def setstowmode_command(
    tmc: TMCFacade, dishes: DishesFacade, event_tracer: TangoEventTracer
):
    """
    Test the SetStowMode command on DishLeafNode.

    This function tests the transition from STANDBY_FP to STANDBY_LP and then
    to STOW mode on a DishLeafNode device.

    Args:
        tmc: TMC facade for accessing TMC devices
        dishes: Dishes facade for accessing dish devices
        event_tracer: Event tracer for subscribing and verifying events
    """
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
    result_stow, unique_id_stow = dish_leaf_node.SetStowMode()

    LOGGER.info(f"Command ID: {unique_id_stow} Returned result: {result_stow}")

    assert_that(event_tracer).within_timeout(
        ASSERTIONS_TIMEOUT
    ).has_change_event_occurred(
        dish_leaf_node,
        "longRunningCommandResult",
        (unique_id[0], COMMAND_COMPLETED),
    )


def stow_while_configuring(
    tmc: TMCFacade,
    dishes: DishesFacade,
    event_tracer: TangoEventTracer,
):
    """
    Test stowing a dish while it is in the process of configuring.

    This function tests the ability to issue a SetStowMode command while a dish
    is transitioning to OPERATE mode during configuration.

    Args:
        tmc: TMC facade for accessing TMC devices
        dishes: Dishes facade for accessing dish devices
        event_tracer: Event tracer for subscribing and verifying events
    """
    dish_leaf_node = tmc.dish_leaf_node_list[0]
    dish_master = dishes.dish_master_dict["dish_001"]

    # Load the dish configuration JSON
    dish_json_str = get_input_str(
        join(
            dirname(__file__),
            "..",
            "data",
            "dish_leaf_node",
            "dishleafnode_configure.json",
        )
    )
    dish_json = json.loads(dish_json_str)

    dish_master.SetDirectDishMode(DishMode.STANDBY_LP)
    event_tracer.subscribe_event(dish_leaf_node, "dishMode")
    event_tracer.subscribe_event(dish_leaf_node, "pointingState")
    event_tracer.subscribe_event(dish_leaf_node, "longRunningCommandResult")

    assert_that(event_tracer).within_timeout(
        ASSERTIONS_TIMEOUT
    ).has_change_event_occurred(
        dish_leaf_node, "dishMode", DishMode.STANDBY_LP
    )

    result_fp, unique_id_fp = dish_leaf_node.SetStandbyFPMode()
    assert_that(event_tracer).within_timeout(
        ASSERTIONS_TIMEOUT
    ).has_change_event_occurred(
        dish_leaf_node, "dishMode", DishMode.STANDBY_FP
    )

    assert result_fp[0] == ResultCode.QUEUED

    assert_that(event_tracer).within_timeout(
        ASSERTIONS_TIMEOUT
    ).has_change_event_occurred(
        dish_leaf_node,
        "longRunningCommandResult",
        (unique_id_fp[0], COMMAND_COMPLETED),
    )

    result_config, unique_id_config = dish_leaf_node.Configure(
        json.dumps(dish_json)
    )
    assert result_config[0] == ResultCode.QUEUED
    LOGGER.info(
        f"Command ID: {unique_id_config} Returned result: {result_config}"
    )

    assert_that(event_tracer).within_timeout(
        ASSERTIONS_TIMEOUT
    ).has_change_event_occurred(dish_leaf_node, "dishMode", DishMode.OPERATE)

    result_stow, unique_id_stow = dish_leaf_node.SetStowMode()
    LOGGER.info(f"Command ID: {unique_id_stow} Returned result: {result_stow}")

    assert result_stow == ResultCode.STARTED

    assert_that(event_tracer).within_timeout(
        ASSERTIONS_TIMEOUT
    ).has_change_event_occurred(dish_leaf_node, "dishMode", DishMode.STOW)

    assert_that(event_tracer).within_timeout(
        ASSERTIONS_TIMEOUT
    ).has_change_event_occurred(
        dish_leaf_node,
        "longRunningCommandResult",
        (unique_id_stow[0], COMMAND_COMPLETED),
    )


# @pytest.mark.aki
@pytest.mark.SKA_mid
def test_stow_while_configuring(
    tmc: TMCFacade, dishes: DishesFacade, event_tracer
):
    """
    Test case for stowing a dish while it is configuring.

    Args:
        tmc: TMC facade fixture
        dishes: Dishes facade fixture
        event_tracer: Event tracer fixture
        json_factory: Factory fixture for creating JSON configuration strings
    """
    stow_while_configuring(tmc, dishes, event_tracer)


@pytest.mark.aki
@pytest.mark.SKA_mid
def test_setstowmode_command(
    tmc: TMCFacade, dishes: DishesFacade, event_tracer
):
    """
    Test case for the SetStowMode command functionality.

    Args:
        tmc: TMC facade fixture
        dishes: Dishes facade fixture
        event_tracer: Event tracer fixture
    """
    setstowmode_command(tmc, dishes, event_tracer)


@pytest.mark.aki
@pytest.mark.SKA_mid
def test_auto_stow_gust_speed(tmc: TMCFacade, event_tracer):
    """
    Test automatic stowing triggered by gust wind speed exceeding threshold.

    Verifies that the dish automatically stows when gust wind speed exceeds
    the configured maximum allowed gust wind speed threshold.

    Args:
        tmc: TMC facade fixture
        event_tracer: Event tracer fixture for verifying status changes
    """
    dish_leaf_node = tmc.dish_leaf_node_list[0]
    event_tracer.subscribe_event(dish_leaf_node, "stowStatus")
    event_tracer.subscribe_event(dish_leaf_node, "dishMode")
    event_tracer.subscribe_event(dish_leaf_node, "longRunningCommandResult")
    _reset_stow_mode(dish_leaf_node, event_tracer)

    dish_leaf_node.maxAllowedGustWindpeed = 22.0
    dish_leaf_node.gustWindspeedMeasurementTimeWindow = 4
    simulate_windspeed(22, 24, 15)

    assert_that(event_tracer).within_timeout(
        ASSERTIONS_TIMEOUT
    ).has_change_event_occurred(
        dish_leaf_node, "stowStatus", StowStatus.STOW_STARTED
    )
    assert_that(event_tracer).within_timeout(
        ASSERTIONS_TIMEOUT
    ).has_change_event_occurred(
        dish_leaf_node, "stowStatus", StowStatus.STOW_COMPLETED
    )


@pytest.mark.aki
@pytest.mark.SKA_mid
def test_auto_stow_wind_speed(tmc: TMCFacade, event_tracer):
    """
    Test automatic stowing triggered by mean wind speed exceeding threshold.

    Verifies that the dish automatically stows when the mean wind speed over
    a measurement time window exceeds the configured maximum threshold.

    Args:
        tmc: TMC facade fixture
        event_tracer: Event tracer fixture for verifying status changes
    """

    dish_leaf_node = tmc.dish_leaf_node_list[0]
    event_tracer.subscribe_event(dish_leaf_node, "stowStatus")
    event_tracer.subscribe_event(dish_leaf_node, "dishMode")
    event_tracer.subscribe_event(dish_leaf_node, "longRunningCommandResult")
    _reset_stow_mode(dish_leaf_node, event_tracer)

    dish_leaf_node.maxAllowedWindspeed = 16.0
    dish_leaf_node.meanWindspeedMeasurementTimeWindow = 10.0
    simulate_windspeed(16, 18, 10)

    assert_that(event_tracer).within_timeout(
        ASSERTIONS_TIMEOUT
    ).has_change_event_occurred(
        dish_leaf_node, "stowStatus", StowStatus.STOW_STARTED
    )
    assert_that(event_tracer).within_timeout(
        ASSERTIONS_TIMEOUT
    ).has_change_event_occurred(
        dish_leaf_node, "stowStatus", StowStatus.STOW_COMPLETED
    )


@pytest.mark.aki
@pytest.mark.SKA_mid
def test_auto_stow_ops_speed(tmc: TMCFacade, event_tracer):
    """
    Test automatic stowing triggered by operational wind speed
    exceeding threshold.

    Verifies that the dish automatically stows when operational wind speed
    exceeds the maximum allowed operational wind speed threshold.

    Args:
        tmc: TMC facade fixture
        event_tracer: Event tracer fixture for verifying status changes
    """
    dish_leaf_node = tmc.dish_leaf_node_list[0]
    event_tracer.subscribe_event(dish_leaf_node, "stowStatus")
    event_tracer.subscribe_event(dish_leaf_node, "dishMode")
    event_tracer.subscribe_event(dish_leaf_node, "longRunningCommandResult")
    _reset_stow_mode(dish_leaf_node, event_tracer)

    dish_leaf_node.maxAllowedOpsWindspeed = 5.0
    dish_leaf_node.WindspeedMeasurementTimeWindow = 10.0
    simulate_windspeed(6, 7, 10)

    assert_that(event_tracer).within_timeout(
        ASSERTIONS_TIMEOUT
    ).has_change_event_occurred(
        dish_leaf_node, "stowStatus", StowStatus.STOW_STARTED
    )
    assert_that(event_tracer).within_timeout(
        ASSERTIONS_TIMEOUT
    ).has_change_event_occurred(
        dish_leaf_node, "stowStatus", StowStatus.STOW_COMPLETED
    )


@pytest.mark.aki
@pytest.mark.SKA_mid
def test_auto_stow_ops_perc_speed(tmc: TMCFacade, event_tracer):
    """
    Test automatic stowing triggered by wind speed percentage difference.

    Verifies that the dish automatically stows when the difference between
    operational wind speeds exceeds the configured percentage threshold.

    Args:
        tmc: TMC facade fixture
        event_tracer: Event tracer fixture for verifying status changes
    """
    dish_leaf_node = tmc.dish_leaf_node_list[0]
    event_tracer.subscribe_event(dish_leaf_node, "stowStatus")
    event_tracer.subscribe_event(dish_leaf_node, "dishMode")
    event_tracer.subscribe_event(dish_leaf_node, "longRunningCommandResult")
    _reset_stow_mode(dish_leaf_node, event_tracer)

    dish_leaf_node.maxAllowedWindspeedDifference = 5.0
    dish_leaf_node.maxAllowedOpsMeanWindspeedMeasurementTimeWindow = 10.0

    simulate_windspeed(10, 11, 3)
    simulate_windspeed(12, 13, 1)
    simulate_windspeed(20, 25, 1)

    assert_that(event_tracer).within_timeout(
        ASSERTIONS_TIMEOUT
    ).has_change_event_occurred(
        dish_leaf_node, "stowStatus", StowStatus.STOW_STARTED
    )
    assert_that(event_tracer).within_timeout(
        ASSERTIONS_TIMEOUT
    ).has_change_event_occurred(
        dish_leaf_node, "stowStatus", StowStatus.STOW_COMPLETED
    )


@pytest.mark.aki
@pytest.mark.SKA_mid
def test_auto_stow_max_temp(tmc: TMCFacade, event_tracer):
    """
    Test automatic stowing triggered by maximum temperature threshold.

    Verifies that the dish automatically stows when the temperature exceeds
    the configured maximum temperature threshold.

    Args:
        tmc: TMC facade fixture
        event_tracer: Event tracer fixture for verifying status changes
    """
    dish_leaf_node = tmc.dish_leaf_node_list[0]
    event_tracer.subscribe_event(dish_leaf_node, "stowStatus")
    event_tracer.subscribe_event(dish_leaf_node, "dishMode")
    event_tracer.subscribe_event(dish_leaf_node, "longRunningCommandResult")
    _reset_stow_mode(dish_leaf_node, event_tracer)

    dish_leaf_node.maxTemperatureThreshold = 35
    simulate_temperature(35, 36, 2)

    assert_that(event_tracer).within_timeout(
        ASSERTIONS_TIMEOUT
    ).has_change_event_occurred(
        dish_leaf_node, "stowStatus", StowStatus.STOW_STARTED
    )
    assert_that(event_tracer).within_timeout(
        ASSERTIONS_TIMEOUT
    ).has_change_event_occurred(
        dish_leaf_node, "stowStatus", StowStatus.STOW_COMPLETED
    )


@pytest.mark.aki
@pytest.mark.SKA_mid
def test_auto_stow_temp_delta(tmc: TMCFacade, event_tracer):
    """
    Test automatic stowing triggered by temperature delta over time.

    Verifies that the dish automatically stows when the temperature change
    over a specified time window exceeds the configured threshold.

    Args:
        tmc: TMC facade fixture
        event_tracer: Event tracer fixture for verifying status changes
    """
    dish_leaf_node = tmc.dish_leaf_node_list[0]
    event_tracer.subscribe_event(dish_leaf_node, "stowStatus")
    event_tracer.subscribe_event(dish_leaf_node, "dishMode")
    event_tracer.subscribe_event(dish_leaf_node, "longRunningCommandResult")
    _reset_stow_mode(dish_leaf_node, event_tracer)
    # sometimes in pipeline it takes more time.
    dish_leaf_node.timeDelta = 10.0
    dish_leaf_node.temperatureDelta = 20.0

    simulate_temperature(10, 11, 2)
    simulate_temperature(15, 20, 2)
    simulate_temperature(31, 35, 6)

    assert_that(event_tracer).within_timeout(
        ASSERTIONS_TIMEOUT
    ).has_change_event_occurred(
        dish_leaf_node, "stowStatus", StowStatus.STOW_STARTED
    )
    assert_that(event_tracer).within_timeout(
        ASSERTIONS_TIMEOUT
    ).has_change_event_occurred(
        dish_leaf_node, "stowStatus", StowStatus.STOW_COMPLETED
    )
    dish_leaf_node.set_timeout_millis(5000)

    dish_leaf_node.timeDelta = 1000.0


def _reset_stow_mode(
    dish_leaf_node: tango.DeviceProxy, event_tracer: TangoEventTracer
):
    """
    Resets the DishMode to StandbyFP.
    """
    if dish_leaf_node.stowStatus == StowStatus.STOW_STARTED:
        assert_that(event_tracer).within_timeout(
            ASSERTIONS_TIMEOUT
        ).has_change_event_occurred(
            dish_leaf_node, "stowStatus", StowStatus.STOW_COMPLETED
        )
    if dish_leaf_node.stowStatus == StowStatus.STOW_COMPLETED:
        result, unique_id = dish_leaf_node.SetStandbyFPMode()

        LOGGER.debug("Command id: %s | Returned result: %s", unique_id, result)
        assert result[0] == ResultCode.QUEUED

        assert_that(event_tracer).within_timeout(
            ASSERTIONS_TIMEOUT
        ).has_change_event_occurred(
            dish_leaf_node,
            "longRunningCommandResult",
            (unique_id[0], COMMAND_COMPLETED),
        )

        assert_that(event_tracer).within_timeout(
            ASSERTIONS_TIMEOUT
        ).has_change_event_occurred(
            dish_leaf_node, "dishMode", DishMode.STANDBY_FP
        )
