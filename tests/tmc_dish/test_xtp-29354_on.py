"""Test module for TMC-DISH On functionality"""


import pytest
from pytest_bdd import parsers, scenario, then, when
from tango import DevState

from tests.resources.test_support.enum import DishMode

<<<<<<< HEAD

<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
=======
# @pytest.mark.xfail(reason="Enable when SKB-292, SKB-293 are resolved")
@pytest.mark.skip
>>>>>>> e92adc1c (SAH-1536: Update test case)
=======
@pytest.mark.skip
>>>>>>> a69408bc (SAH-1536: Test only xtp-42658)
=======
>>>>>>> 2ee3ddf7 (SAH-1536: Enable skipped tmc-dish tests)
=======
@pytest.mark.skip
>>>>>>> c60c8729 (SAH-1536: Test only test case for long sequence)
=======
>>>>>>> 1fc6a549 (SAH-1536: Enable all the tmc-dish tests)
=======
@pytest.mark.skip
>>>>>>> a58b1b2a (SAH-1564: Test pipline)
@pytest.mark.tmc_dish
@scenario(
    "../features/tmc_dish/xtp-29354_on.feature",
    "Start up Telescope with TMC and DISH devices",
)
def test_tmc_dish_startup_telescope():
    """
    Test case to verify TMC-DISH StartUp functionality
    """


@when("I start up the telescope")
def move_dish_to_on(central_node_mid, event_recorder):
    """
    A method to put Telescope ON

    Args:
        central_node_mid: Fixture for a TMC CentralNode wrapper class
        event_recorder: Fixture for EventRecorder class
    """

    event_recorder.subscribe_event(
        central_node_mid.central_node, "telescopeState"
    )
    for dish_id in ["SKA001", "SKA036", "SKA063", "SKA100"]:
        event_recorder.subscribe_event(
            central_node_mid.dish_master_dict[dish_id], "dishMode"
        )
        event_recorder.subscribe_event(
            central_node_mid.dish_leaf_node_dict[dish_id], "dishMode"
        )

    assert event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "telescopeState",
        DevState.OFF,
    )

    central_node_mid.move_to_on()


@then(
    parsers.parse("DishMaster {dish_ids} must transition to STANDBY-FP mode")
)
def check_dish_is_on(central_node_mid, event_recorder, dish_ids):
    """
    Method to check dishMode after invoking
    telescopeOn command on central node

    Args:
        central_node_mid: Fixture for a TMC CentralNode wrapper class
        event_recorder: Fixture for EventRecorder class
        dish_ids (str): Comma-separated IDs of DISH components.
    """
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


@then("telescope state is ON")
def check_telescope_state(central_node_mid, event_recorder):
    """
    Method to check if TMC central node is ON

    Args:
        central_node_mid: Fixture for a TMC CentralNode wrapper class
        event_recorder: Fixture for EventRecorder class
    """
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

    assert event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "telescopeState",
        DevState.ON,
    )
