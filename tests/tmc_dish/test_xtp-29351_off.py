"""Test module for TMC-DISH Off functionality"""

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
<<<<<<< HEAD
<<<<<<< HEAD
=======
@pytest.mark.xfail(reason="Enable when SKB-292, SKB-293 are resolved")
>>>>>>> 254f9823 (SAH-1536: disable test case)
=======
=======

>>>>>>> a90de43d (SAH-1564: Test pipline)
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
=======
>>>>>>> 8ac35da0 (SAH-1564: Revert change)
@pytest.mark.tmc_dish
@scenario(
    "../features/tmc_dish/xtp-29351_off.feature",
    "Shut down with TMC and DISH devices",
)
def test_tmc_dish_shutdown_telescope():
    """
    Test case to verify TMC-DISH ShutDown functionality
    """


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
