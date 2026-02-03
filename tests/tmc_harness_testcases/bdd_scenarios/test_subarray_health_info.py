import json
import logging

import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import HealthState, ObsState

from tests.resources.test_harness.helpers import (
    get_device_simulators,
    prepare_json_args_for_commands,
    set_desired_health_state,
    wait_and_validate_device_attribute_value,
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


@when(
    parsers.parse(
        "band {active_band} is active and band {unavailable_band} "
        "becomes unavailable"
    )
)
def make_band_unavailable(
    subarray_node, simulator_factory, active_band, unavailable_band
):
    (
        _,
        _,
        dish_master_sim_1,
        dish_master_sim_2,
        dish_master_sim_3,
        dish_master_sim_4,
    ) = get_device_simulators(simulator_factory)

    # 1. Start with all bands available
    capability_dict = {
        "B1": CapabilityStates.OPERATE_FULL,
        "B2": CapabilityStates.OPERATE_FULL,
        "B3": CapabilityStates.OPERATE_FULL,
        "B4": CapabilityStates.OPERATE_FULL,
        "B5a": CapabilityStates.OPERATE_FULL,
        "B5b": CapabilityStates.OPERATE_FULL,
    }

    # 2. Make the requested band unavailable
    capability_dict[unavailable_band] = CapabilityStates.UNAVAILABLE

    # 3. Send JSON string to simulator
    dish_master_sim_1.SetDirectCapabilityState(json.dumps(capability_dict))

    logger.info(
        "Band %s set to UNAVAILABLE while active band is %s",
        unavailable_band,
        active_band,
    )

    # 4. Dish health expectation
    expected_dish_health = (
        HealthState.FAILED
        if active_band == unavailable_band
        else HealthState.DEGRADED
    )

    assert wait_and_validate_device_attribute_value(
        subarray_node.dish_leaf_node_list[0],
        "healthState",
        expected_dish_health,
    ), (
        f"Dish did not reach {expected_dish_health} "
        f"when {unavailable_band} became unavailable"
    )


@then(
    parsers.parse(
        "subarray health state becomes {expected_health_state} "
        "due to unavailable band"
    )
)
def validate_subarray_health_and_info(
    subarray_node, event_recorder, expected_health_state
):
    # Convert string to HealthState enum
    if isinstance(expected_health_state, str):
        expected_health_state = HealthState[expected_health_state]

    # Subscribe to events
    event_recorder.subscribe_event(subarray_node.subarray_node, "healthState")
    event_recorder.subscribe_event(subarray_node.subarray_node, "healthInfo")

    # Validate healthState
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "healthState",
        expected_health_state,
    ), f"Subarray healthState did not become {expected_health_state}"

    # Validate healthInfo
    raw_health_info = subarray_node.subarray_node.healthInfo
    logger.info("Raw Subarray healthInfo: %s", raw_health_info)
    health_info = json.loads(raw_health_info)

    affected_dishes = []
    for dish, entries in health_info.items():
        for entry in entries:
            if isinstance(entry, dict):
                health_state = entry.get("healthState")
                reason = entry.get("reason", "")
            else:
                health_state = None
                reason = str(entry)
            health_state_str = (
                str(health_state) if health_state is not None else ""
            )
            # Check if dish health matches expected
            if (
                expected_health_state.name in health_state_str
                or "UNAVAILABLE" in reason
            ):
                affected_dishes.append((dish, health_state, reason))

    assert affected_dishes, (
        f"No dish reports expected health degradation in Subarray healthInfo. "
        f"Expected={expected_health_state.name}, healthInfo={health_info}"
    )

    for dish, health_state, reason in affected_dishes:
        logger.info(
            "Dish %s affected | healthState=%s | reason=%s",
            dish,
            health_state,
            reason,
        )
