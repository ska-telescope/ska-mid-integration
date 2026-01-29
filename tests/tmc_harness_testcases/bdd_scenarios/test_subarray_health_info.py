import json
import logging

import pytest
from pytest_bdd import given, scenario, then, when
from ska_control_model import HealthState, ObsState

from tests.resources.test_harness.helpers import (
    get_device_simulators,
    prepare_json_args_for_commands,
    set_desired_health_state,
)
from tests.resources.test_harness.utils.enums import CapabilityStates

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pytest.mark.batch2test
@pytest.mark.SKA_mid
@scenario(
    "../features/test_harness/subarray_healthinfo.feature",
    "Dish health failure is reflected in Subarray HealthInfo",
)
def test_subarray_healthinfo():
    """Dish failure propagates to Subarray HealthInfo"""


# -------------------------
# GIVEN STEPS
# -------------------------


@given("Dishes are assigned to Subarray with Health State as OK")
def assign_dishes_to_subarray(
    subarray_node, event_recorder, command_input_factory, simulator_factory
):
    """Assign Dishes to TMC Subarray Device
    Args:
        subarray_node: Subarray Node Fixture object
        event_recorder: Event Recorder class object
        command_input_factory: Command Input Factory class object
        simulator_factory: Simulator Factory Fixture object
    """
    subarray_node.move_to_on()
    subarray_node.force_change_of_obs_state("EMPTY")
    input_json = prepare_json_args_for_commands(
        "assign_resources_mid", command_input_factory
    )

    event_recorder.subscribe_event(subarray_node.subarray_node, "obsState")

    subarray_node.execute_transition("AssignResources", argin=input_json)
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node, "obsState", ObsState.IDLE
    ), "Waiting for subarray node to complete"

    (
        _,
        _,
        dish_master_sim_1,
        dish_master_sim_2,
        dish_master_sim_3,
        dish_master_sim_4,
    ) = get_device_simulators(simulator_factory)
    set_desired_health_state(
        sim_devices_list=[
            dish_master_sim_1,
            dish_master_sim_2,
            dish_master_sim_3,
            dish_master_sim_4,
        ],
        health_state_value=HealthState.OK,
    )


@given("Subarray is configured successfully and Health State remains OK")
def configure_subarray_and_validate_health_ok(
    subarray_node,
    event_recorder,
    command_input_factory,
):
    """Configure Subarray and verify Health State remains OK"""

    input_json = prepare_json_args_for_commands(
        "configure_mid", command_input_factory
    )

    event_recorder.subscribe_event(subarray_node.subarray_node, "obsState")
    event_recorder.subscribe_event(subarray_node.subarray_node, "healthState")

    subarray_node.execute_transition("Configure", argin=input_json)
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.READY,
    ), "Subarray did not reach READY after Configure"

    # Validate Health State remains OK
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "healthState",
        HealthState.OK,
    ), "Subarray HealthState is not OK after Configure"


@when("the requested band becomes unavailable")
def make_band_unavailable(simulator_factory):
    (
        _,
        _,
        dish_master_sim_1,
        dish_master_sim_2,
        dish_master_sim_3,
        dish_master_sim_4,
    ) = get_device_simulators(simulator_factory)

    capability_argin = json.dumps(
        {
            "B1": CapabilityStates.OPERATE_FULL,
            "B2": CapabilityStates.UNAVAILABLE,
            "B3": CapabilityStates.OPERATE_FULL,
            "B4": CapabilityStates.OPERATE_FULL,
            "B5a": CapabilityStates.OPERATE_FULL,
            "B5b": CapabilityStates.OPERATE_FULL,
        }
    )

    for dish_sim in [
        dish_master_sim_1,
        dish_master_sim_2,
        dish_master_sim_3,
        dish_master_sim_4,
    ]:
        dish_sim.SetDirectCapabilityState(capability_argin)


@then("subarray health state becomes FAILED due to unavailable band")
def validate_failed_health(subarray_node, event_recorder):
    """Validate Subarray HealthState becomes FAILED and log healthInfo"""

    # Subscribe to healthInfo updates (safe even if already subscribed)
    event_recorder.subscribe_event(subarray_node.subarray_node, "healthInfo")

    # Fetch healthInfo attribute
    raw_health_info = subarray_node.subarray_node.healthInfo
    logger.info("Raw Subarray healthInfo: %s", raw_health_info)
    # Log full healthInfo clearly
    health_info = json.loads(raw_health_info)

    logger.info(
        "Parsed Subarray healthInfo:\n%s",
        json.dumps(health_info, indent=4),
    )

    # Validate at least one dish is FAILED
    failed_dishes = [
        dish
        for dish, info in health_info.items()
        if info.get("healthState") == "FAILED"
    ]

    assert failed_dishes, (
        "No dish is marked FAILED in Subarray healthInfo "
        "even though band was UNAVAILABLE"
    )

    # Validate failure reason
    for dish in failed_dishes:
        reason = health_info[dish].get("reason", "")
        logger.info(
            "Dish %s FAILED with reason: %s",
            dish,
            reason,
        )
        assert (
            "UNAVAILABLE" in reason
        ), f"Dish {dish} FAILED but reason is incorrect: {reason}"
