"""Verify the telescope state transitions over TMC-CSP.

Verify the telescope state transitions when the following commands are
sent to the telescope central node:

- TelescopeOff
- TelescopeStandby
- TelescopeOn

"""

import pytest
from assertpy import assert_that
from pytest_bdd import given, parsers, scenario, then, when
from ska_integration_test_harness.facades.csp_facade import (
    CSPFacade,  # CSP facade
)
from ska_integration_test_harness.facades.tmc_central_node_facade import (
    TMCCentralNodeFacade,
)
from ska_tango_testing.integration import TangoEventTracer, log_events
from tango import DevState

# Constants
ASSERTIONS_TIMEOUT = 60


# ---------------------------------
# Scenario Definitions
# ---------------------------------


@pytest.mark.tmc_csp_new_ITH
@scenario(
    "../tmc_csp_new_ITH/features/telescope_state.feature",
    "ON to OFF - CMD TelescopeOff",
)
def test_on_to_off():
    """Test transitioning from ON to OFF."""


@pytest.mark.skip(reason="CBF is not supporting STANDBY command")
@pytest.mark.tmc_csp_new_ITH
@scenario(
    "../tmc_csp_new_ITH/features/telescope_state.feature",
    "ON to STANDBY - CMD TelescopeStandby",
)
def test_on_to_standby():
    """Test transitioning from ON to STANDBY."""


@pytest.mark.tmc_csp_new_ITH
@scenario(
    "../tmc_csp_new_ITH/features/telescope_state.feature",
    "OFF to ON - CMD TelescopeOn",
)
def test_off_to_on():
    """Test transitioning from OFF to ON."""


# ---------------------------------
# Given Steps
# ---------------------------------


@given(parsers.parse("a tracked telescope"))
def tracked_telescope(
    event_tracer: TangoEventTracer,
    central_node_facade: TMCCentralNodeFacade,
    csp: CSPFacade,
):
    """A telescope where the event tracking is configured
    to track the telescope state (over TMC central node and CSP devices).
    """
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


@given(parsers.parse("the telescope is in OFF state"))
def telescope_in_off_state(central_node_facade: TMCCentralNodeFacade):
    """Ensure the telescope is in the OFF state."""
    central_node_facade.move_to_off(wait_termination=True)


# ---------------------------------
# When Steps
# ---------------------------------


@when(
    parsers.parse(
        "the TelescopeOff command is sent to the telescope central node"
    )
)
def send_telescope_off_command(
    event_tracer: TangoEventTracer, central_node_facade: TMCCentralNodeFacade
):
    """Send the TelescopeOff command to the telescope."""
    event_tracer.clear_events()
    central_node_facade.move_to_off(wait_termination=False)


@when(
    parsers.parse(
        "the TelescopeStandby command is sent to the telescope central node"
    )
)
def send_telescope_standby_command(
    event_tracer: TangoEventTracer, central_node_facade: TMCCentralNodeFacade
):
    """Send the TelescopeStandby command to the telescope."""
    event_tracer.clear_events()
    central_node_facade.set_standby(wait_termination=False)


@when(
    parsers.parse(
        "the TelescopeOn command is sent to the telescope central node"
    )
)
def send_telescope_on_command(
    event_tracer: TangoEventTracer, central_node_facade: TMCCentralNodeFacade
):
    """Send the TelescopeOn command to the telescope."""
    event_tracer.clear_events()
    central_node_facade.move_to_on(wait_termination=False)


# ---------------------------------
# Then Steps
# ---------------------------------


@then(parsers.parse("the telescope should transition to the OFF state"))
def verify_off_state(
    event_tracer: TangoEventTracer,
    central_node_facade: TMCCentralNodeFacade,
    csp: CSPFacade,
):
    """The telescope and CSP devices transition to the OFF state."""
    assert_that(event_tracer).described_as(
        "The telescope and CSP devices should transition from ON to OFF state."
    ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
        central_node_facade.central_node,
        "telescopeState",
        DevState.OFF,
    ).has_change_event_occurred(
        csp.csp_master,
        "State",
        DevState.OFF,
    )


@then(parsers.parse("the telescope should transition to the STANDBY state"))
def verify_standby_state(
    event_tracer: TangoEventTracer,
    central_node_facade: TMCCentralNodeFacade,
    csp: CSPFacade,
):
    """The telescope and CSP devices transition to the STANDBY state."""
    assert_that(event_tracer).described_as(
        "The telescope and CSP master should transition "
        "to the STANDBY state. "
        "CSP subarray should transition to OFF state."
    ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
        central_node_facade.central_node,
        "telescopeState",
        DevState.STANDBY,
    ).has_change_event_occurred(
        csp.csp_master,
        "State",
        DevState.STANDBY,
    )


@then(parsers.parse("the telescope should transition to the ON state"))
def verify_on_state(
    event_tracer: TangoEventTracer,
    central_node_facade: TMCCentralNodeFacade,
    csp: CSPFacade,
):
    """The telescope and CSP devices transition to the ON state."""
    assert_that(event_tracer).described_as(
        "The telescope and CSP devices should transition " "to the ON state."
    ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
        central_node_facade.central_node,
        "telescopeState",
        DevState.ON,
    ).has_change_event_occurred(
        csp.csp_master,
        "State",
        DevState.ON,
    ).has_change_event_occurred(
        csp.csp_subarray,
        "State",
        DevState.ON,
    )
