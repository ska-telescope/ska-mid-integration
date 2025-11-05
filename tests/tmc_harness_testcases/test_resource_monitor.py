"""
Test case for verifying Resource Monitor updates when SubarrayNode assigned
resources change in MID system.
This test simulates a change in assigned resources and checks that the
ResourceMonitor device reflects the update in its dishesData attribute.
"""
import json
import time

import pytest
from assertpy import assert_that
from pytest_bdd import given, scenario, then, when
from ska_tango_base.control_model import ObsState
from ska_tango_testing.integration import TangoEventTracer, log_events
from tango import DeviceProxy, DevState

from tests.resources.test_harness.central_node_mid import CentralNodeWrapperMid
from tests.resources.test_harness.simulator_factory import SimulatorFactory
from tests.resources.test_harness.utils.common_utils import JsonFactory
from tests.resources.test_harness.utils.enums import SimulatorDeviceType
from tests.resources.test_support.common_utils.tmc_helpers import (
    prepare_json_args_for_centralnode_commands,
)
from tests.resources.test_support.constant import TIMEOUT

RESOURCE_MONITOR_FQDN = "mid-tmc/resource-monitor/01"


@pytest.mark.SKA_mid
@scenario(
    "../features/resource_monitor.feature",
    "Test Resource Monitoring updates when SubarrayNode attributes change",
)
def test_resource_monitor_updates_mid():
    """BDD scenario for verifying Resource Monitor update on MID."""


@given("the MID TMC and ResourceMonitor devices are ON")
def given_tmc_on(
    event_tracer: TangoEventTracer,
    central_node_mid: CentralNodeWrapperMid,
):
    """
    Ensure that the TMC and ResourceMonitor devices are available and ON.
    """
    resource_monitor = DeviceProxy(RESOURCE_MONITOR_FQDN)

    event_tracer.subscribe_event(
        central_node_mid.central_node, "telescopeState"
    )
    event_tracer.subscribe_event(central_node_mid.subarray_node, "obsState")
    event_tracer.subscribe_event(
        central_node_mid.subarray_node, "assignedResources"
    )
    event_tracer.subscribe_event(resource_monitor, "dishesData")

    log_events(
        {
            central_node_mid.central_node: ["telescopeState"],
            central_node_mid.subarray_node: ["obsState", "assignedResources"],
            resource_monitor: ["dishesData"],
        }
    )

    central_node_mid.move_to_on()

    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION: TMC CentralNode should be ON"
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_mid.central_node, "telescopeState", DevState.ON
    )

    given_tmc_on.resource_monitor = resource_monitor
    event_tracer.clear_events()


@given("the MID subarray is in IDLE obsState")
def given_subarray_idle(
    command_input_factory: JsonFactory,
    event_tracer: TangoEventTracer,
    central_node_mid: CentralNodeWrapperMid,
):
    """
    Assign resources to move subarray to IDLE state.
    """
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_mid", command_input_factory
    )

    central_node_mid.perform_action("AssignResources", assign_input_json)

    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION: Subarray must reach IDLE obsState after "
        "AssignResources"
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_mid.subarray_node, "obsState", ObsState.IDLE
    )

    event_tracer.clear_events()


@when("a change is triggered in the SubarrayNode assigned resources")
def when_assigned_resources_changed(
    central_node_mid: CentralNodeWrapperMid,
    simulator_factory: SimulatorFactory,
):
    """
    Simulate a change in SubarrayNode assigned resources using CSP simulator.
    """
    csp_sim = simulator_factory.get_or_create_simulator_device(
        SimulatorDeviceType.CSP_SUBARRAY_DEVICE
    )

    assigned_resources = {
        "subarray_beam_ids": ["1"],
        "receptor_ids": ["0001", "0002", "0003"],
        "frequency_band": "5a",
        "channels": [32],
    }

    csp_sim.SetDirectassignedResources(json.dumps(assigned_resources))
    when_assigned_resources_changed.assigned_resources = assigned_resources
    time.sleep(5)


@then("the ResourceMonitoring dishesData attribute should reflect the change")
def then_verify_resource_monitor_update(event_tracer: TangoEventTracer):
    """
    Verify that ResourceMonitor dishesData reflects the updated assigned
    resources.
    """
    resource_monitor = given_tmc_on.resource_monitor
    assigned_resources = when_assigned_resources_changed.assigned_resources

    expected_dishes_data = {
        "dishes": {
            receptor_id: {"subarray_allocation": 1}
            for receptor_id in assigned_resources["receptor_ids"]
        }
    }

    assert_that(event_tracer).described_as(
        "ResourceMonitor did not update dishesData after assigned resources "
        "change"
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        resource_monitor, "dishesData", json.dumps(expected_dishes_data)
    )
