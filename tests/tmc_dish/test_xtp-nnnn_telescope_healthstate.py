"""Test case for verifying TMC TelescopeHealthState transition """
import logging
import time

import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_tango_base.control_model import HealthState
from tango import DevState

from tests.resources.test_support.enum import DishMode

LOGGER = logging.getLogger(__name__)


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


@given("a Telescope consisting of TMC, DISH, simulated CSP and simulated SDP")
def given_a_telescope(central_node_mid):
    """
    Given a TMC
    """
    assert central_node_mid.csp_master.ping() > 0
    assert central_node_mid.sdp_master.ping() > 0
    for dish_id in ["SKA001", "SKA036", "SKA063", "SKA100"]:
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
    central_node_mid, event_recorder, health_state
):
    """Method to set the health state of specified simulator devices."""

    spfrx_fqdn = (
        "tango://tango-databaseds.dish-lmc-1.svc.cluster.local:10000/"
        "mid-dish/simulator-spfrx/SKA001"
    )
    central_node_mid.dish1_db.delete_device(spfrx_fqdn)
    LOGGER.info("spfrx deleted")
    central_node_mid.dish1_admin_dev_proxy.RestartServer()
    LOGGER.info("dish is restarted ")
    # Added a wait for the completion of dish device deletion from TANGO
    # database and the dish device restart
    time.sleep(5)
    # asserting dishmanager healthstate
    event_recorder.subscribe_event(
        central_node_mid.dish_master_dict["SKA001"], "healthState"
    )
    LOGGER.info("subscribed health state for dishmanager ")
    assert event_recorder.has_change_event_occurred(
        central_node_mid.dish_master_dict["SKA001"],
        "healthState",
        HealthState[health_state],
    ), f"Expected healthState to be \
        {HealthState[health_state]}"

    event_recorder.subscribe_event(
        central_node_mid.dish_leaf_node_dict["SKA001"], "healthState"
    )
    LOGGER.info("subscribed health state for dishln ")
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
