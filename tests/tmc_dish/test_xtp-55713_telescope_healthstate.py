"""Test case for verifying TMC TelescopeHealthState transition"""
import logging
import time

import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_tango_base.control_model import HealthState
from tango import DevState
from tango.db import DbDevInfo

from tests.resources.test_support.enum import DishMode


@pytest.mark.tmc_dish
@scenario(
    "../features/tmc_dish/xtp-55713_telescope_healthstate.feature",
    "Verify CentralNode TelescopeHealthState",
)
def test_tmc_TMC_healthstate():
    """
    Test case verifying TMC TelescopeHealthState transition based on DISH-LMC
    subsystems HealthState
    """


@given("a Telescope consisting of TMC, DISH, simulated CSP and simulated SDP")
def given_a_telescope(central_node_mid):
    """Given a TMC

    Args:
        central_node_mid : A fixture for CentralNode tango device class
    """
    assert central_node_mid.csp_master.ping() > 0
    assert central_node_mid.sdp_master.ping() > 0
    for dish_id in ["SKA001", "SKA036", "SKA063", "SKA100"]:
        assert central_node_mid.dish_master_dict[dish_id].ping() > 0
        assert central_node_mid.dish_leaf_node_dict[dish_id].ping() > 0


@given("the Telescope is in ON state")
def turn_on_telescope(central_node_mid, event_recorder):
    """A method to put Telescope ON

    Args:
        central_node_mid : A fixture for CentralNode tango device class
        event_recorder: A fixture for EventRecorder class_
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


@when(parsers.parse("the {device} health state changes to {health_state}"))
def set_simulator_devices_health_states(
    central_node_mid, event_recorder, health_state
):
    """Method to set the health state of specified simulator devices.

    Args:
        central_node_mid : A fixture for CentralNode tango device class
        event_recorder: A fixture for EventRecorder class_
        health_state (str): healthState value
    """
    # transitioning dishmanger (SKA001) healthstate to UNKNOWN by deleting
    # deleting spfrx device
    central_node_mid.dish1_db.delete_device(central_node_mid.spfrx_fqdn)

    central_node_mid.spfrx1_admin_dev_proxy.RestartServer()

    # Added a wait for the completion of spfrx1 device deletion from TANGO
    # database and the spfrx1 device restart
    time.sleep(5)

<<<<<<< HEAD:tests/tmc_dish/test_xtp-nnnn_telescope_healthstate.py
<<<<<<< HEAD
    # check_spfrx1_info = central_node_mid.dish1_db.get_device_info(
    #     "mid-dish/simulator-spfrx/SKA001"
    # )
    # LOGGER.info("spfrx1 device info is: %s", check_spfrx1_info)
=======
    check_spfrx1_info = central_node_mid.dish1_db.get_device_info(
        "mid-dish/simulator-spfrx/SKA001"
    )
    LOGGER.info("spfrx1 device info is: %s", check_spfrx1_info)
>>>>>>> 5a5415f6 (SAH-1536: Fix the error in the test.)

    # asserting dishmanager healthstate
=======
    # asserting UNKOWN healthstate for dishmaster and dishleafnode
>>>>>>> 2ee3ddf7 (SAH-1536: Enable skipped tmc-dish tests):tests/tmc_dish/test_xtp-55713_telescope_healthstate.py
    event_recorder.subscribe_event(
        central_node_mid.dish_master_dict["SKA001"], "healthState"
    )

    assert event_recorder.has_change_event_occurred(
        central_node_mid.dish_master_dict["SKA001"],
        "healthState",
        HealthState[health_state],
    ), f"Expected healthState to be \
        {HealthState[health_state]}"

    event_recorder.subscribe_event(
        central_node_mid.dish_leaf_node_dict["SKA001"], "healthState"
    )

    assert event_recorder.has_change_event_occurred(
        central_node_mid.dish_leaf_node_dict["SKA001"],
        "healthState",
        HealthState[health_state],
    ), f"Expected healthState to be \
        {HealthState[health_state]}"


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

    event_recorder.subscribe_event(
        central_node_mid.central_node, "telescopeHealthState"
    )

    assert event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "telescopeHealthState",
        HealthState[telescope_health_state],
    ), f"Expected telescopeHealthState to be \
        {HealthState[telescope_health_state]}"

    # Add Dish device back to DB
    dev_info = DbDevInfo()
    dev_info.name = central_node_mid.spfrx_fqdn
    dev_info._class = central_node_mid.spfrx1_dev_class
    dev_info.server = central_node_mid.spfrx1_dev_server
    central_node_mid.dish1_db.add_device(dev_info)
    central_node_mid.spfrx1_admin_dev_proxy.RestartServer()
    # When device restarts it can take around 15 sec to up again
    # so wait for the spfrx1 device to start and dish1 dishMode
    # to be in proper state
    time.sleep(15)

    logging.info("asserting health state at end")
    assert event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "telescopeHealthState",
        HealthState.OK,
    ), "Expected Central Node telescopeHealthState to be OK"
