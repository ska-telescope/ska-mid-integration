"""Test module for TMC-CSP ShutDown functionality"""
import pytest
from pytest_bdd import given, scenario, then, when
from tango import DevState

from tests.resources.test_harness.helpers import get_master_device_simulators
from tests.test_harness2.sut_actions.move_to_off import MoveToOff
from tests.test_harness2.sut_actions.move_to_on import MoveToOn
from tests.test_harness2.sut_actions.set_standby import SetStandby
from tests.test_harness2.sut_structure.sut_wrapper import TelescopeWrapper


@pytest.mark.tmc_csp
@scenario(
    "../features/tmc_csp/xtp_29250_off.feature",
    "Turn Off Telescope with real TMC and CSP devices",
)
def test_tmc_csp_telescope_off_harness_refactor2():
    """
    Test case to verify TMC-CSP ShutDown functionality
    """


@pytest.mark.tmc_csp
@scenario(
    "../features/tmc_csp/xtp_29251_standby.feature",
    "Standby the Telescope with real TMC and CSP devices",
)
def test_tmc_csp_telescope_standby_harness_refactor2():
    """
    Test case to verify TMC-CSP ShutDown functionality
    """


@given(
    "a Telescope consisting of TMC, CSP, simulated DISH and simulated"
    + " SDP devices"
)
def given_the_sut(sut: TelescopeWrapper, simulator_factory):
    """
    Given a TMC

    Args:
        simulator_factory: fixture for SimulatorFactory class,
        which provides simulated subarray and master devices
    """
    # Add dish 4 when SKB-266 is resolved
    (
        _,
        sdp_master_sim,
        dish_master_sim_1,
        dish_master_sim_2,
        dish_master_sim_3,
        dish_master_sim_4,
    ) = get_master_device_simulators(simulator_factory)

    assert sut.tmc.central_node.ping() > 0
    assert sut.sdp.sdp_master.ping() > 0
    assert sut.sdp.sdp_subarray.ping() > 0

    # NOTE: why this?
    assert sdp_master_sim.ping() > 0
    assert dish_master_sim_1.ping() > 0
    assert dish_master_sim_2.ping() > 0
    assert dish_master_sim_3.ping() > 0
    assert dish_master_sim_4.ping() > 0

    # NOTE: will ever the "ON" string match the DevState.ON?
    if sut.tmc.telescope_state != "ON":
        # central_node_mid.move_to_on()
        sut.execute_action(MoveToOn())

    # sut.execute_action(factory.create_move_to_on())
    # move_to_on(sut)
    # sut.move_to_on()

    # NOTE: SUT in this context is TMC and CSP. The others are technically
    # not part of the SUT. They are part of the test environment.

    # telescope? Better

    # telescope.tmc.send_move_to_on_command()

    # (Inside send_move_to_on_command())

    # TMC sends the command ON to
    # telescope.tmc.central_node.MoveToOn()


@given("telescope is in ON state")
def check_telescope_state_is_on(sut: TelescopeWrapper, event_recorder):
    """A method to check if telescopeState is on"""
    event_recorder.subscribe_event(sut.tmc.central_node, "telescopeState")
    assert event_recorder.has_change_event_occurred(
        sut.tmc.central_node,
        "telescopeState",
        DevState.ON,
        lookahead=15,
    )


@when("I switch off telescope")
def move_sdp_to_off(sut: TelescopeWrapper):
    """A method to put tmc to OFF"""
    # central_node_mid.move_to_off()
    sut.execute_action(MoveToOff())


@when("I standby the telescope")
def move_sdp_to_standby(sut: TelescopeWrapper):
    """A method to put tmc to STANDBY"""
    # central_node_mid.set_standby()
    sut.execute_action(SetStandby())


@then("the CSP must go to OFF state")
def check_csp_is_off(sut: TelescopeWrapper, event_recorder):
    """A method to check CSP's State"""
    event_recorder.subscribe_event(sut.csp.csp_master, "State")
    event_recorder.subscribe_event(sut.csp.csp_subarray, "State")
    assert event_recorder.has_change_event_occurred(
        sut.csp.csp_master,
        "State",
        DevState.OFF,
    )
    assert event_recorder.has_change_event_occurred(
        sut.csp.csp_subarray,
        "State",
        DevState.OFF,
    )


@then("telescope state is OFF")
def check_telescope_state_off(sut: TelescopeWrapper, event_recorder):
    """A method to check CentralNode.telescopeState"""
    assert event_recorder.has_change_event_occurred(
        sut.tmc.central_node,
        "telescopeState",
        DevState.OFF,
    )


@then("the csp controller must go to standby state")
def check_csp_master_is_moved_to_standby(
    sut: TelescopeWrapper, event_recorder
):
    """A method to check CSP controllers State"""
    event_recorder.subscribe_event(sut.csp.csp_master, "State")
    assert event_recorder.has_change_event_occurred(
        sut.csp.csp_master, "State", DevState.STANDBY, lookahead=15
    )


@then("the csp subarray must go to off state")
def check_csp_subarray_is_moved_to_off(sut: TelescopeWrapper, event_recorder):
    """A method to check CSP Subarray's State"""
    event_recorder.subscribe_event(sut.csp.csp_subarray, "State")
    assert event_recorder.has_change_event_occurred(
        # central_node_mid.subarray_devices["csp_subarray"],
        sut.csp.csp_subarray,
        "State",
        DevState.OFF,
        lookahead=10,
    )


@then("telescope state is STANDBY")
def check_telescope_state_is_standby(sut: TelescopeWrapper, event_recorder):
    """A method to check CentralNode.telescopeState"""
    assert event_recorder.has_change_event_occurred(
        # sut.central_node,
        sut.tmc.central_node,
        "telescopeState",
        DevState.STANDBY,
    )
