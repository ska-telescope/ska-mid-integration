"""Test module for TMC-CSP ShutDown functionality"""
import pytest
from assertpy import assert_that
from pytest_bdd import given, scenario, then, when
from ska_tango_testing.integration import TangoEventTracer, log_events
from tango import DevState

from tests.test_harness3.telescope_facades.csp_facade import CSPFacade
from tests.test_harness3.telescope_facades.dishes_facade import DishesFacade
from tests.test_harness3.telescope_facades.sdp_facade import SDPFacade
from tests.test_harness3.telescope_facades.tmc_central_node_facade import (
    TMCCentralNodeFacade,
)

ASSERTIONS_TIMEOUT = 60


@pytest.mark.skip("Redundant test")
@pytest.mark.tmc_csp
@scenario(
    "../features/tmc_csp/xtp_29250_off.feature",
    "Turn Off Telescope with real TMC and CSP devices",
)
def test_tmc_csp_telescope_off_harness_refactor3():
    """
    Test case to verify TMC-CSP ShutDown functionality
    """


@pytest.mark.skip("Redundant test")
@pytest.mark.tmc_csp
@scenario(
    "../features/tmc_csp/xtp_29251_standby.feature",
    "Standby the Telescope with real TMC and CSP devices",
)
def test_tmc_csp_telescope_standby_harness_refactor3():
    """
    Test case to verify TMC-CSP ShutDown functionality
    """


@given(
    "a Telescope consisting of TMC, CSP, simulated DISH and simulated"
    + " SDP devices"
)
def given_the_sut(
    central_node_facade: TMCCentralNodeFacade,
    sdp: SDPFacade,
    csp: CSPFacade,
    dishes: DishesFacade,
):
    """Given a TMC."""
    assert central_node_facade.central_node.ping() > 0

    assert sdp.sdp_master.ping() > 0
    assert sdp.sdp_subarray.ping() > 0

    assert csp.csp_master.ping() > 0
    assert csp.csp_subarray.ping() > 0

    assert dishes.dish_master_list[0].ping() > 0
    assert dishes.dish_master_list[1].ping() > 0
    assert dishes.dish_master_list[2].ping() > 0
    assert dishes.dish_master_list[3].ping() > 0

    # what about something like: central_node_facade.health_check() ?


@given("telescope is in ON state")
def check_telescope_state_is_on(
    central_node_facade: TMCCentralNodeFacade,
):
    """A method to check if telescopeState is on"""
    central_node_facade.move_to_on(wait_termination=True)


@when("I switch off telescope")
def move_sdp_to_off(
    central_node_facade: TMCCentralNodeFacade,
    csp: CSPFacade,
    event_tracer: TangoEventTracer,
):
    """A method to put tmc to OFF"""
    event_tracer.subscribe_event(
        central_node_facade.central_node, "telescopeState"
    )
    event_tracer.subscribe_event(csp.csp_master, "State")
    event_tracer.subscribe_event(csp.csp_subarray, "State")
    log_events(
        {
            central_node_facade.central_node: ["telescopeState"],
            csp.csp_master: ["State"],
            csp.csp_subarray: ["State"],
        }
    )

    central_node_facade.move_to_off(wait_termination=False)


@when("I standby the telescope")
def move_sdp_to_standby(
    central_node_facade: TMCCentralNodeFacade,
    csp: CSPFacade,
    event_tracer: TangoEventTracer,
):
    """A method to put tmc to STANDBY"""
    event_tracer.subscribe_event(
        central_node_facade.central_node, "telescopeState"
    )
    event_tracer.subscribe_event(csp.csp_master, "State")
    event_tracer.subscribe_event(csp.csp_subarray, "State")
    log_events(
        {
            central_node_facade.central_node: ["telescopeState"],
            csp.csp_master: ["State"],
            csp.csp_subarray: ["State"],
        }
    )

    central_node_facade.set_standby(wait_termination=False)


@then("the CSP must go to OFF state")
def check_csp_is_off(csp: CSPFacade, event_tracer):
    """A method to check CSP's State"""
    assert_that(event_tracer).described_as(
        "CSP Master device "
        f"({csp.csp_master}) "
        "State attribute value is supposed to be OFF."
    ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
        csp.csp_master,
        "State",
        DevState.OFF,
    )
    assert_that(event_tracer).described_as(
        "CSP Subarray device "
        f"({csp.csp_subarray}) "
        "State attribute value is supposed to be OFF."
    ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
        csp.csp_subarray,
        "State",
        DevState.OFF,
    )


@then("telescope state is OFF")
def check_telescope_state_off(
    central_node_facade: TMCCentralNodeFacade, event_tracer
):
    """A method to check CentralNode.telescopeState"""
    assert_that(event_tracer).described_as(
        "TMC Central Node device "
        f"({central_node_facade.central_node}) "
        "telescopeState attribute value is supposed to be OFF."
    ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
        central_node_facade.central_node,
        "telescopeState",
        DevState.OFF,
    )


@then("the csp controller must go to standby state")
def check_csp_master_is_moved_to_standby(csp: CSPFacade, event_tracer):
    """A method to check CSP controllers State"""
    assert_that(event_tracer).described_as(
        "CSP Master device "
        f"({csp.csp_master}) "
        "State attribute value is supposed to be STANDBY."
    ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
        csp.csp_master,
        "State",
        DevState.STANDBY,
    )


@then("the csp subarray must go to off state")
def check_csp_subarray_is_moved_to_off(csp: CSPFacade, event_tracer):
    """A method to check CSP Subarray's State"""
    assert_that(event_tracer).described_as(
        "CSP Subarray device "
        f"({csp.csp_subarray}) "
        "State attribute value is supposed to be OFF."
    ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
        csp.csp_subarray,
        "State",
        DevState.OFF,
    )


@then("telescope state is STANDBY")
def check_telescope_state_is_standby(
    central_node_facade: TMCCentralNodeFacade, event_tracer
):
    """A method to check CentralNode.telescopeState"""
    assert_that(event_tracer).described_as(
        "TMC Central Node device "
        f"({central_node_facade.central_node}) "
        "telescopeState attribute value is supposed to be STANDBY."
    ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
        central_node_facade.central_node,
        "telescopeState",
        DevState.STANDBY,
    )
