"""Test case for verifying TMC TelescopeHealthState transition """

import os

import pytest
from pytest_bdd import given, parsers, scenario, then, when

# from ska_tango_base.control_model import ObsState
from tango import DevState

# from tests.resources.test_harness.helpers import (
#     get_device_simulator_with_given_name,
# )
from tests.resources.test_harness.simulator_factory import SimulatorFactory

# from tests.resources.test_harness.helpers import (
#     prepare_json_args_for_centralnode_commands,
#     prepare_json_args_for_commands,
# )
# from tests.resources.test_harness.subarray_node import SubarrayNodeWrapper
# from tests.resources.test_harness.utils.common_utils import JsonFactory
# from tests.resources.test_support.common_utils.result_code import ResultCode
from tests.resources.test_support.enum import DishMode

# from tests.resources.test_harness.event_recorder import EventRecorder


spfrx1_dev_name = os.getenv("SPFRX_NAME_1")


@pytest.mark.skip
@pytest.mark.tmc_dish
@scenario(
    "../features/tmc_dish/xtp-nnnn_telescope_healthstate.feature",
    "Verify CentralNode TelescopeHealthState",
)
def test_tmc_TMC_healthstate():
    """
    Test case verifying TMC TelescopeHealthState transition based on DISH-LMC
    subsystems HealthState
    """


@given(
    parsers.parse(
        "a Telescope consisting of TMC, DISH {dish_ids},"
        + " simulated CSP and simulated SDP"
    )
)
def given_a_telescope(central_node_mid, dish_ids):
    """
    Given a TMC
    """
    assert central_node_mid.csp_master.ping() > 0
    assert central_node_mid.sdp_master.ping() > 0
    for dish_id in dish_ids.split(","):
        assert central_node_mid.dish_master_dict[dish_id].ping() > 0
        assert central_node_mid.dish_leaf_node_dict[dish_id].ping() > 0


@given("the Telescope is in ON state")
def turn_on_telescope(central_node_mid, event_recorder):
    """
    A method to put Telescope ON
    """
    central_node_mid.move_to_on()
    event_recorder.subscribe_event(central_node_mid.csp_master, "State")
    event_recorder.subscribe_event(central_node_mid.sdp_master, "State")

    assert event_recorder.has_change_event_occurred(
        central_node_mid.csp_master,
        "State",
        DevState.ON,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_mid.sdp_master,
        "State",
        DevState.ON,
    )

    for dish_id in ["SKA001", "SKA036", "SKA063", "SKA100"]:
        event_recorder.subscribe_event(
            central_node_mid.dish_master_dict[dish_id], "dishMode"
        )
        event_recorder.subscribe_event(
            central_node_mid.dish_leaf_node_dict[dish_id], "dishMode"
        )

        assert event_recorder.has_change_event_occurred(
            central_node_mid.dish_master_dict[dish_id],
            "dishMode",
            DishMode.STANDBY_FP,
        )
        assert event_recorder.has_change_event_occurred(
            central_node_mid.dish_leaf_node_dict[dish_id],
            "dishMode",
            DishMode.STANDBY_FP,
        )

    event_recorder.subscribe_event(
        central_node_mid.central_node, "telescopeState"
    )

    assert event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "telescopeState",
        DevState.ON,
    )


@when(parsers.parse("the {devices} health state changes to {health_state}"))
def set_simulator_devices_health_states(
    devices: str, health_state: str, simulator_factory: SimulatorFactory
):
    """Method to set the health state of specified simulator devices.

    Args:
        devices (list): Names of the devices whose health state will change.
        health_state (list): The new health states for the devices.
        simulator_factory (SimulatorFactory): Fixture for SimulatorFactory
          class.
    """
    pass
    # # Split the devices string into individual devices
    # devices_list = devices.split(",")
    # health_state_list = health_state.split(",")

    # sim_devices_list = get_device_simulator_with_given_name(
    #     simulator_factory, devices_list
    # )
    # for sim_device, sim_health_state_val in list(
    #     zip(sim_devices_list, health_state_list)
    # ):
    #     # Check if the device is not the SDP controller
    #     if sim_device.dev_name not in [sdp_master]:
    #      sim_device.SetDirectHealthState(HealthState[sim_health_state_val])


@then(parsers.parse("the telescope health state is {telescope_health_state}"))
def check_telescope_health_state(
    central_node_mid, event_recorder, telescope_health_state
):
    """A method to check CentralNode.telescopehealthState attribute
    change after aggregation

    Args:
        central_node_mid : A fixture for CentralNode tango device class
        event_recorder: A fixture for EventRecorder class_
        telescope_health_state (str): telescopehealthState value
    """
    pass
    # event_recorder.subscribe_event(
    #     central_node_mid.central_node, "telescopeHealthState"
    # )

    # assert event_recorder.has_change_event_occurred(
    #     central_node_mid.central_node,
    #     "telescopeHealthState",
    #     HealthState[telescope_health_state],
    # ), f"Expected telescopeHealthState to be \
    #     {HealthState[telescope_health_state]}"
