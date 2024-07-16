"""Test module for TMC-DISH Off functionality"""

import pytest
from pytest_bdd import parsers, scenario, then, when
from tango import DevState

from tests.resources.test_support.enum import DishMode

@pytest.mark.skip(reason="Test being fix in SAH-1564")
@pytest.mark.tmc_dish
@scenario(
    "../features/tmc_dish/xtp-29351_off.feature",
    "Shut down with TMC and DISH devices",
)
def test_tmc_dish_shutdown_telescope():
    """
    Test case to verify TMC-DISH ShutDown functionality
    """


<<<<<<< HEAD
=======
@given(
    parsers.parse(
        "a Telescope consisting of TMC, DISH {dish_ids},"
        + " simulated CSP and simulated SDP is in ON state"
    )
)
def check_tmc_and_dish_is_on(central_node_mid, event_recorder, dish_ids):
    """
    Given a TMC , DISH , simulated CSP and simulated in ON state
    """
    assert central_node_mid.csp_master.ping() > 0
    assert central_node_mid.sdp_master.ping() > 0
    for dish_id in dish_ids.split(","):
        assert central_node_mid.dish_master_dict[dish_id].ping() > 0
        assert central_node_mid.dish_leaf_node_dict[dish_id].ping() > 0

    central_node_mid.move_to_on()

    for dish_id in dish_ids.split(","):
        event_recorder.subscribe_event(
            central_node_mid.dish_master_dict[dish_id], "dishMode"
        )
        event_recorder.subscribe_event(
            central_node_mid.dish_leaf_node_dict[dish_id], "dishMode"
        )
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

    for dish_id in dish_ids.split(","):
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


>>>>>>> 8db544db (SAH-1558: Debug the errors in the tests.)
@when("I switch off the telescope")
def turn_off_telescope(central_node_mid):
    """
    Invoke telescopeOff on TMC

    Args:
        central_node_mid: Fixture for a TMC CentralNode wrapper class
    """
    central_node_mid.move_to_off()


@then(
    parsers.parse("DishMaster {dish_ids} must transition to STANDBY-LP mode")
)
def check_dish_state(central_node_mid, event_recorder, dish_ids):
    """
    Method to check dishMode

    Args:
        central_node_mid: Fixture for a TMC CentralNode wrapper class
        event_recorder: Fixture for EventRecorder class
        dish_ids (str): Comma-separated IDs of DISH components.
    """
    for dish_id in dish_ids.split(","):
        assert event_recorder.has_change_event_occurred(
            central_node_mid.dish_master_dict[dish_id],
            "dishMode",
            DishMode.STANDBY_LP,
        )
        assert event_recorder.has_change_event_occurred(
            central_node_mid.dish_leaf_node_dict[dish_id],
            "dishMode",
            DishMode.STANDBY_LP,
        )


@then("telescope is OFF")
def check_telescopeOff_state(central_node_mid, event_recorder):
    """
    Method to check telescope is turned OFF

    Args:
        central_node_mid: Fixture for a TMC CentralNode wrapper class
        event_recorder: Fixture for EventRecorder class
    """
    assert event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "telescopeState",
        DevState.OFF,
    )
