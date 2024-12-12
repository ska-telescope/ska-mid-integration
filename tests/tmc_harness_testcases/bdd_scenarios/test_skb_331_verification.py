"""Test module to test delay functionality."""
import json
import logging

import pytest
from pytest_bdd import given, scenario, then, when
from ska_control_model import ObsState

from tests.resources.test_harness.central_node_mid import CentralNodeWrapperMid
from tests.resources.test_harness.event_recorder import EventRecorder
from tests.resources.test_harness.helpers import (
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
)
from tests.resources.test_harness.subarray_node import SubarrayNodeWrapper
from tests.resources.test_harness.utils.common_utils import JsonFactory

# from tango import DevState


LOGGER = logging.getLogger(__name__)


@pytest.mark.sah1630
@pytest.mark.SKA_mid
@scenario(
    "../features/test_harness/xtp-45178_skb_331.feature",
    "Verify the output_host and output_port"
    + " in configure json send to csp subarray",
)
def test_csp_configure_json() -> None:
    """
    Test case to verify csp configure json.
    """


@given("the telescope is in ON state")
def check_telescope_is_in_on_state(
    central_node_mid: CentralNodeWrapperMid, event_recorder: EventRecorder
) -> None:
    """Ensure telescope is in ON state."""
    central_node_mid.move_to_on()
    event_recorder.subscribe_event(
        central_node_mid.central_node, "telescopeState"
    )
    # assert event_recorder.has_change_event_occurred(
    #     central_node_mid.central_node,
    #     "telescopeState",
    #     DevState.ON,
    # )


@given("TMC subarray in ObsState IDLE")
def move_subarray_node_to_idle_obsstate(
    central_node_mid: CentralNodeWrapperMid,
    event_recorder: EventRecorder,
    command_input_factory: JsonFactory,
) -> None:
    """Move TMC Subarray to IDLE ObsState."""
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_mid", command_input_factory
    )
    assign_input = json.loads(assign_input_json)
    central_node_mid.store_resources(json.dumps(assign_input))

    event_recorder.subscribe_event(central_node_mid.subarray_node, "obsState")
    assert event_recorder.has_change_event_occurred(
        central_node_mid.subarray_node,
        "obsState",
        ObsState.IDLE,
    )


@when("I invoke configure command on TMC subarray")
def invoke_configure_command(
    subarray_node: SubarrayNodeWrapper,
    command_input_factory: JsonFactory,
    event_recorder: EventRecorder,
) -> None:
    """
    Invokes Configure command and checks whether subarray is in ObsState READY
    """
    configure_input_json = prepare_json_args_for_commands(
        "configure_mid", command_input_factory
    )
    subarray_node.store_configuration_data(configure_input_json)
    event_recorder.subscribe_event(subarray_node.subarray_node, "obsState")


@then(
    "TMC subarray invokes configure on csp with json"
    + " containing output_host and output_port"
)
def check_json_content(subarray_node):
    input_json = subarray_node.subarray_devices[
        "csp_subarray"
    ].commandCallInfo[-1][-1]
    fsp_list = json.loads(input_json)["midcbf"]["correlation"][
        "processing_regions"
    ]
    for fsp_config in fsp_list:
        assert "output_host" in fsp_config.keys()
        assert "output_port" in fsp_config.keys()


@then("the TMC subarray transitions to ObsState READY")
def check_obsState_ready(subarray_node, event_recorder):
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "obsState",
        ObsState.READY,
    )
