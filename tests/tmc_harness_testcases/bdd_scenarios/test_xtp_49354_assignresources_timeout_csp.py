"""Test module to test Assignresources while SDP is defective."""
import json

import pytest
from pytest_bdd import scenario, then, when
from ska_tango_testing.mock.placeholders import Anything

from tests.resources.test_harness.central_node_mid import CentralNodeWrapperMid
from tests.resources.test_harness.constant import (
    INTERMEDIATE_STATE_DEFECT,
    RESET_DEFECT,
)
from tests.resources.test_harness.helpers import (
    prepare_json_args_for_centralnode_commands,
)
from tests.resources.test_harness.simulator_factory import SimulatorFactory
from tests.resources.test_harness.utils.common_utils import JsonFactory
from tests.resources.test_harness.utils.enums import SimulatorDeviceType


@pytest.mark.SKA_mid
@scenario(
    "../features/test_harness/"
    + "xtp_49354_assignresources_timeout_csp.feature",
    "Verify error propogation with failure on CSP Subarray while invoking"
    + " AssignResources",
)
def test_assignrsources_timeout_csp() -> None:
    """
    Test case to verify ReleaseResources timeout on CSP Subarray.
    """


# from conftest.py
# @given("the telescope is in ON state")


@when("I issue the AssignResources to TMC while CSP subarray is set defective")
def invoke_assignresources_command_with_csp_subarray_defective(
    central_node_mid: CentralNodeWrapperMid,
    command_input_factory: JsonFactory,
    simulator_factory: SimulatorFactory,
) -> None:
    pytest.csp_sim = simulator_factory.get_or_create_simulator_device(
        SimulatorDeviceType.MID_CSP_DEVICE
    )
    # Set csp defective
    pytest.csp_sim.SetDefective(json.dumps(INTERMEDIATE_STATE_DEFECT))
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_mid", command_input_factory
    )
    assign_input = json.loads(assign_input_json)
    pytest.command_result = central_node_mid.perform_action(
        "AssignResources", json.dumps(assign_input)
    )


@then("Exception is propagated to TMC on longRunningCommandResult")
def check_timeout_error(
    central_node_mid: CentralNodeWrapperMid, event_recorder
):
    """A method to check SubarrayNode.longRunningCommandResult attribute
    change for exception

    Args:
        subarray_node : A fixture for SubarrayNode tango device class
        event_recorder: A fixture for EventRecorder class
    """
    event_recorder.subscribe_event(
        central_node_mid.central_node, "longRunningCommandResult"
    )
    assertion_data = event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "longRunningCommandResult",
        (pytest.command_result[1][0], Anything),
        lookahead=15,
    )
    exception_message = "Timeout has occurred, command failed"
    assert (
        exception_message
        in json.loads(assertion_data["attribute_value"][1])[1]
    )

    pytest.csp_sim.SetDefective(RESET_DEFECT)
