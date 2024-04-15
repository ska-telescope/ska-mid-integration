"""Test TMC-CSP Sucessive AssignResources functionality"""
import ast
import logging

import pytest
from pytest_bdd import given, parsers, scenario, when
from ska_control_model import ObsState
from tango import DevState

from tests.resources.test_harness.helpers import (
    check_subarray_instance,
    prepare_json_args_for_centralnode_commands,
)

LOGGER = logging.getLogger(__name__)


@pytest.mark.tmc_csp
@scenario(
    "../features/tmc_csp/incremental_assignresources.feature",
    "Validate succesive AssignResources command",
)
def test_tmc_csp_reassign_resources():
    """
    Test case to verify sucessive AssignResources on TMC-CSP
    """


@given(parsers.parse("TMC subarray {subarray_id} is in EMPTY ObsState"))
def subarray_is_in_empty_obsstate(
    central_node_mid,
    event_recorder,
    subarray_id,
    subarray_node,
):
    """Method to move subarray into the IDLE ObsState."""
    assert central_node_mid.central_node.ping() > 0
    assert central_node_mid.subarray_devices["csp_subarray"].ping() > 0
    event_recorder.subscribe_event(
        central_node_mid.central_node, "telescopeState"
    )
    event_recorder.subscribe_event(
        central_node_mid.subarray_devices["csp_subarray"], "obsState"
    )
    event_recorder.subscribe_event(subarray_node.subarray_node, "obsState")

    central_node_mid.move_to_on()

    check_subarray_instance(central_node_mid.subarray_node, subarray_id)
    assert event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "telescopeState",
        DevState.ON,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.EMPTY,
    )


@when(
    parsers.parse(
        "I invoke First AssignResources on TMC subarray {subarray_id} with "
        + "{receptors1} on TMC subarray {subarray_id}"
    )
)
def invoke_first_assign_Resources(
    central_node_mid, subarray_id, command_input_factory, receptors1
):
    """Execute second assign resource"""

    check_subarray_instance(central_node_mid.subarray_node, subarray_id)
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_mid", command_input_factory
    )
    LOGGER.info(f"input resources:{receptors1}")
    LOGGER.info(f"type input resources:{type(receptors1)}")
    resources = ast.literal_eval(receptors1)
    LOGGER.info(f"input resources>>>>:{resources}")
    LOGGER.info(f"type input resources>>>>:{type(resources)}")

    assign_input_json["dish"]["receptor_ids"] = resources

    LOGGER.info(f"assignresources: {assign_input_json}")
    central_node_mid.store_resources(assign_input_json)
    assert 0
