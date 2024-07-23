"""Test module to verify timeout error propogation from SDP Subarray"""
import json

import pytest
from pytest_bdd import given, scenario, then, when
from ska_tango_testing.mock.placeholders import Anything

from tests.resources.test_harness.constant import (
    COMMAND_NOT_ALLOWED_DEFECT,
    RESET_DEFECT,
    tmc_sdp_subarray_leaf_node,
)
from tests.resources.test_harness.helpers import prepare_json_args_for_commands
from tests.resources.test_harness.subarray_node import SubarrayNodeWrapper
from tests.resources.test_harness.utils.common_utils import JsonFactory
from tests.resources.test_harness.utils.enums import SimulatorDeviceType


@pytest.mark.configure
@pytest.mark.SKA_mid
@scenario(
    "../features/test_harness/xtp_49327_sdp_subarray_"
    + "error_propogation.feature",
    "Verify CommandNotAllowed error propogation with defective SDP Subarray",
)
def test_sdp_subarray_configure_timeout_and_error_propagation():
    """
    Test case to verify CommandNotAllowed error propogation
    """


# from conftest.py
# @given("the telescope is in ON state")


@given("SDP subarray is set with command not allowed defect")
def set_sdp_subarray_defective(simulator_factory):
    """A method to set command not allowed defect
    for SDP Subarray

    Args:
        simulator_factory: fixture for SimulatorFactory class,
        which provides simulated subarray and master devices
    """
    pytest.sdp_sim = simulator_factory.get_or_create_simulator_device(
        SimulatorDeviceType.MID_SDP_DEVICE
    )
    # Set SDP subarray defective
    pytest.sdp_sim.SetDefective(json.dumps(COMMAND_NOT_ALLOWED_DEFECT))


# @when("I issue the Configure command from TMC SubarrayNode")
# def invoke_configure(
#     central_node_mid: CentralNodeWrapperMid,
#     command_input_factory: JsonFactory,
# ) -> None:
#     """
#     Invokes AssignResources command
#     """
#     assign_input_json = prepare_json_args_for_centralnode_commands(
#         "assign_resources_mid", command_input_factory
#     )
#     pytest.command_result = central_node_mid.perform_action(
#         "AssignResources", assign_input_json
#     )


@when("I issue the Configure command from TMC SubarrayNode")
def invoke_configure(
    subarray_node: SubarrayNodeWrapper,
    command_input_factory: JsonFactory,
) -> None:
    """
    Invokes Configure command
    """
    configure_input_json = prepare_json_args_for_commands(
        "configure_mid", command_input_factory
    )
    pytest.command_result = subarray_node.perform_action(
        "Configure", configure_input_json
    )


@then(
    "CommandNotAllowed exception is propagated to TMC Subarraynode "
    + "on longRunningCommandResult"
)
def check_timeout_error(subarray_node, event_recorder):
    """A method to check SubarrayNode.longRunningCommandResult attribute
    change for exception

    Args:
        subarray_node : A fixture for SubarrayNode tango device class
        event_recorder: A fixture for EventRecorder class
    """
    event_recorder.subscribe_event(
        subarray_node.subarray_node, "longRunningCommandResult"
    )
    assertion_data = event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "longRunningCommandResult",
        (pytest.command_result[1][0], Anything),
        lookahead=15,
    )
    exception_message = (
        "Exception occurred on the following devices:"
        + f" {tmc_sdp_subarray_leaf_node}:"
        " ska_tmc_common.exceptions.CommandNotAllowed:"
        " Command is not allowed\n\n"
    )
    assert (
        exception_message
        in json.loads(assertion_data["attribute_value"][1])[1]
    )

    pytest.sdp_sim.SetDefective(RESET_DEFECT)
