"""Test Subarray Health State
"""
import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_tango_base.control_model import HealthState, ObsState

from tests.resources.test_harness.helpers import (
    get_device_simulator_with_given_name,
    get_device_simulators,
    prepare_json_args_for_commands,
    set_desired_health_state,
)


@pytest.mark.SKA_mid
@scenario(
    "../features/test_harness/subarray_health_state.feature",
    "Subarray Health State should be Failed or Degraded when one or more "
    "devices health state is Failed or Degraded",
)
def test_subarray_health_state_with_csp_and_sdp():
    """
    Test Subarray Health is Failed or degraded when csp or sdp is
    FAILED or DEGRADED
    """


@pytest.mark.SKA_mid
@scenario(
    "../features/test_harness/subarray_health_state.feature",
    "Subarray Health State Changes based on Simulator Device Health State",
)
def test_subarray_health_state_with_dish(subarray_node):
    """
    Test Subarray Health is Failed or degraded when dish master device is
    failed and degraded
    """


@given("csp subarray, sdp subarray and dish masters health state is OK")
def given_simulator_device_health_state_is_ok(simulator_factory):
    """Set Simulator Health State to OK
    Args:
        simulator_factory: Simulator Factory Fixture object
    """
    (
        csp_sa_sim,
        sdp_sa_sim,
        dish_master_sim_1,
        dish_master_sim_2,
        dish_master_sim_3,
        dish_master_sim_4,
    ) = get_device_simulators(simulator_factory)

    set_desired_health_state(
        sim_devices_list=[
            csp_sa_sim,
            sdp_sa_sim,
            dish_master_sim_1,
            dish_master_sim_2,
            dish_master_sim_3,
            dish_master_sim_4,
        ],
        health_state_value=HealthState.OK,
    )


@given("csp subarray, sdp subarray health state is OK")
def given_csp_sdp_device_health_state_is_ok(simulator_factory):
    """Set CSP and SDP device health state to OK
    Args:
        simulator_factory: Simulator Factory Fixture object
    """
    (
        csp_sa_sim,
        sdp_sa_sim,
        _,
        _,
        _,
        _,
    ) = get_device_simulators(simulator_factory)

    set_desired_health_state(
        sim_devices_list=[csp_sa_sim, sdp_sa_sim],
        health_state_value=HealthState.OK,
    )


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


@when(
    parsers.parse(
        "The {Devices} health state changes to {Device_Health_State}"
    )
)
def set_devices_health_state(simulator_factory, Devices, Device_Health_State):
    """Set Devices health state as per provided argument
    Args:
        simulator_factory: Simulator Factory Fixture object
        Devices: List of Device name to set health state
        Device_Health_State: List of Device Health Set
    """
    # Get simulator device objects
    devices = Devices.split(",")
    device_simulator_list = get_device_simulator_with_given_name(
        simulator_factory, devices
    )

    # Set Device Health State
    health_state_list = Device_Health_State.split(",")
    for device_simulator, device_health_state in zip(
        device_simulator_list, health_state_list
    ):
        device_simulator.SetDirectHealthState(HealthState[device_health_state])


@then(parsers.parse("subarray health state is {Subarray_Health_State}"))
def validate_expected_subarray_health_state(
    subarray_node, event_recorder, Subarray_Health_State
):
    """Validate Expected Health state for Subarray Node
    Args:
        subarray_node: Subarray Node Fixture object
        event_recorder: Event Recorder class object
        Subarray_Health_State: Expected Subarray Health state
    """
    event_recorder.subscribe_event(subarray_node.subarray_node, "healthState")

    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "healthState",
        HealthState[Subarray_Health_State],
    ), f"Expected Subarray Node HealthState to be {Subarray_Health_State}"
