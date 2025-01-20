"""Test module to test Assignresources timeout on SDP Subarray."""
import json
import logging

import pytest
from pytest_bdd import scenario, then, when
from ska_ser_logging import configure_logging

from tests.resources.test_harness.central_node_mid import CentralNodeWrapperMid
from tests.resources.test_harness.event_recorder import EventRecorder
from tests.resources.test_harness.helpers import (
    get_device_simulators,
    prepare_json_args_for_centralnode_commands,
)
from tests.resources.test_harness.simulator_factory import SimulatorFactory
from tests.resources.test_harness.utils.common_utils import JsonFactory
from tests.resources.test_support.common_utils.result_code import ResultCode

configure_logging(logging.DEBUG)
LOGGER = logging.getLogger(__name__)


@pytest.mark.test1
@pytest.mark.batch1
@pytest.mark.SKA_mid
@scenario(
    "../features/test_harness/"
    + "xtp_49356_assignresources_timeout_sdp.feature",
    "Verify error propogation with failure on SDP Subarray while invoking"
    + " AssignResources",
)
def test_assignrsources_timeout_sdp() -> None:
    """
    Test case to verify Assignresources timeout on SDP Subarray.
    """


# from conftest.py
# @given("the telescope is in ON state")


@when("I issue the AssignResources to TMC while SDP subarray is set defective")
def invoke_assignresources_command_with_sdp_subarray_defective(
    central_node_mid: CentralNodeWrapperMid,
    command_input_factory: JsonFactory,
    simulator_factory: SimulatorFactory,
) -> None:
    _, sdp_sim, _, _, _, _ = get_device_simulators(simulator_factory)
    # Set sdp defective
    sdp_sim.SetDelayInfo(json.dumps({"AssignResources": 170}))

    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_mid", command_input_factory
    )
    assign_input = json.loads(assign_input_json)
    pytest.command_result = central_node_mid.perform_action(
        "AssignResources", json.dumps(assign_input)
    )


@then("Exception is propagated to TMC on longRunningCommandResult")
def check_timeout_error(
    central_node_mid: CentralNodeWrapperMid,
    event_recorder: EventRecorder,
    simulator_factory: SimulatorFactory,
):
    """A method to check SubarrayNode longRunningCommandResult attribute
    change for exception

    """
    _, sdp_sim, _, _, _, _ = get_device_simulators(simulator_factory)
    event_recorder.subscribe_event(
        central_node_mid.central_node, "longRunningCommandResult"
    )
    event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "longRunningCommandResult",
        (
            pytest.command_result[1][0],
            json.dumps(
                [ResultCode.FAILED, "Timeout has occurred, command failed"]
            ),
        ),
        lookahead=25,
    )

    sdp_sim.ResetDelayInfo()
