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
=======
@pytest.mark.skip
>>>>>>> efe6d5dd (SAH-1564: Run only long sequence test for tmc-dish interface)
=======
>>>>>>> bb18efd6 (SAH-1567: Code cleanup)
=======
@pytest.mark.skip(reason="Test being fix in SAH-1564")
>>>>>>> 438706f0 (SAH-1536: Update test case)
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
<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> d683a756 (SAH-1558: Debug the errors in the tests.)
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
<<<<<<< HEAD
<<<<<<< HEAD

=======
        logging.info(
            "Dish Manager FQDN: %s",
            central_node_mid.dish_master_dict[dish_id].get_fqdn(),
        )
        logging.info(
            "Dish Manager Info: %s",
            central_node_mid.dish_master_dict[dish_id].info(),
        )
        logging.info(
            "Dish LN FQDN: %s",
            central_node_mid.dish_leaf_node_dict[dish_id].get_fqdn(),
        )
        logging.info(
            "Dish LN Info: %s",
            central_node_mid.dish_leaf_node_dict[dish_id].info(),
        )

    assert 0
>>>>>>> d683a756 (SAH-1558: Debug the errors in the tests.)
=======

>>>>>>> 33b25903 (SAH-1558: Debug the errors in the tests.)
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
<<<<<<< HEAD
=======
>>>>>>> 415d590c (SAH-1536: Resolve review comments)
=======
>>>>>>> d683a756 (SAH-1558: Debug the errors in the tests.)
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
