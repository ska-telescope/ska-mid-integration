"""
Test case for verifying Resource Monitor updates when SubarrayNode assigned
resources change in the system.

This test verifies that the ResourceMonitor device correctly updates its
dishesData attribute after resources are assigned and released through the
SubarrayNode.
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
from tests.resources.test_harness.helpers import (
    prepare_json_args_for_centralnode_commands,
)
from tests.resources.test_harness.utils.common_utils import JsonFactory
from tests.resources.test_support.constant import TIMEOUT

RESOURCE_MONITOR_FQDN = "mid-tmc/resource-monitor/01"


@pytest.mark.batch1
@pytest.mark.SKA_mid
@scenario(
    "../features/resource_monitor.feature",
    "Check ResourceMonitor updates after resource assignment and release",
)
def test_resource_monitor_updates():
    """BDD scenario for verifying Resource Monitor updates."""


@given("the TMC and ResourceMonitor devices are ON")
def given_tmc_on(
    event_tracer: TangoEventTracer, central_node_mid: CentralNodeWrapperMid
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
        "FAILED ASSUMPTION: CentralNode should be ON"
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_mid.central_node, "telescopeState", DevState.ON
    )

    pytest.resource_monitor = resource_monitor
    event_tracer.clear_events()


@given("the subarray has assigned resources and is in IDLE obsState")
def given_subarray_idle(
    command_input_factory: JsonFactory,
    event_tracer: TangoEventTracer,
    central_node_mid: CentralNodeWrapperMid,
):
    """
    Assign resources and verify that the subarray reaches IDLE state.
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

    pytest.assign_input_json = assign_input_json
    time.sleep(5)


@then(
    "the ResourceMonitor dishesData attribute should reflect the assigned "
    "resources"
)
def then_verify_resource_monitor_update(event_tracer: TangoEventTracer):
    """
    Verify that ResourceMonitor dishesData reflects the assigned resources.
    """
    resource_monitor = pytest.resource_monitor
    assign_input_json = pytest.assign_input_json
    assigned_resources = (
        json.loads(assign_input_json).get("dish").get("receptor_ids", [])
    )

    expected_dishes_data = {
        "dishes": {
            receptor_id: {"subarray_allocation": 1, "availability": True}
            for receptor_id in assigned_resources
        }
    }
    results = json.dumps(expected_dishes_data)
    time.sleep(2)
    assert_that(event_tracer).described_as(
        "ResourceMonitor dishesData attribute value should update"
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        resource_monitor, "dishesData", results
    )


@when("all assigned resources are released")
def when_release_all_resources(
    event_tracer: TangoEventTracer,
    central_node_mid: CentralNodeWrapperMid,
    command_input_factory: JsonFactory,
):
    """Release all previously assigned resources."""
    release_input_json = prepare_json_args_for_centralnode_commands(
        "release_resources_mid", command_input_factory
    )
    _, pytest.unique_id = central_node_mid.perform_action(
        "ReleaseResources", release_input_json
    )
    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION: Subarray should return to EMPTY obsState after "
        "ReleaseAllResources"
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_mid.subarray_node, "obsState", ObsState.EMPTY
    )
    time.sleep(5)


@then(
    "the ResourceMonitor dishesData attribute should reflect the updated "
    "state after resource release"
)
def then_verify_resource_monitor_empty(event_tracer: TangoEventTracer):
    """Verify that ResourceMonitor dishesData becomes empty after release."""
    resource_monitor = pytest.resource_monitor
    assign_input_json = pytest.assign_input_json
    previously_assigned_dishes = (
        json.loads(assign_input_json).get("dish").get("receptor_ids", [])
    )

    expected_dishes_data = {
        "dishes": {
            receptor_id: {"subarray_allocation": -1, "availability": True}
            for receptor_id in previously_assigned_dishes
        }
    }
    results = json.dumps(expected_dishes_data)

    time.sleep(5)

    assert_that(event_tracer).described_as(
        "ResourceMonitor dishesData attribute should be empty after "
        "ReleaseAllResources"
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        resource_monitor, "dishesData", results
    )
