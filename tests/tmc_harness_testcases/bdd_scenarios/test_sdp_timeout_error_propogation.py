"""Test module to verify timeout error propogation from SDP Subarray"""
import json

import pytest
from pytest_bdd import scenario, then, when
from ska_tango_testing.mock.placeholders import Anything

from tests.resources.test_harness.constant import (
    OBS_STATE_CONFIGURING_STUCK_DEFECT,
    RESET_DEFECT,
)
from tests.resources.test_harness.event_recorder import EventRecorder
from tests.resources.test_harness.helpers import prepare_json_args_for_commands
from tests.resources.test_harness.subarray_node import SubarrayNodeWrapper
from tests.resources.test_harness.utils.common_utils import JsonFactory
from tests.resources.test_harness.utils.enums import SimulatorDeviceType


@pytest.mark.configure
@pytest.mark.SKA_mid
@scenario(
    "../features/test_harness/xtp_49327.feature",
    "Verify timeout error propogation with defective SDP Subarray",
)
def test_sdp_subarray_configure_timeout_and_error_propagation():
    """
    Test case to verify error propogation for
    timeout occured on SDP Subarray
    """


# from conftest.py
# @given("the telescope is in ON state")


# from conftest.py
# @given("TMC subarray is in ObsState IDLE")


@when("SDP subarray is set defective with timeout")
def set_sdp_subarray_defective(simulator_factory):
    """A method to set defect, obsState CONFIGURING
    stuck for SDP Subarray

    Args:
        simulator_factory: fixture for SimulatorFactory class,
        which provides simulated subarray and master devices
    """
    pytest.sdp_sim = simulator_factory.get_or_create_simulator_device(
        SimulatorDeviceType.MID_SDP_DEVICE
    )
    # Set SDP subarray defective
    pytest.sdp_sim.SetDefective(json.dumps(OBS_STATE_CONFIGURING_STUCK_DEFECT))


@then("I issue the Configure command to the TMC subarray")
def invoke_configure(
    subarray_node: SubarrayNodeWrapper,
    command_input_factory: JsonFactory,
    event_recorder: EventRecorder,
) -> None:
    """
    Invokes Configure command
    """
    event_recorder.subscribe_event(
        subarray_node.subarray_node, "longRunningCommandResult"
    )
    configure_input_json = prepare_json_args_for_commands(
        "configure_mid", command_input_factory
    )
    pytest.command_result = subarray_node.execute_transition(
        "Configure", argin=configure_input_json
    )


@then(
    "Timeout error is propagated to TMC subarray on longRunningCommandResult"
)
def check_timeout_error(subarray_node, event_recorder):
    """A method to check SubarrayNode.longRunningCommandResult attribute
    change after timeout error

    Args:
        subarray_node : A fixture for SubarrayNode tango device class
        event_recorder: A fixture for EventRecorder class
    """
    assertion_data = event_recorder.has_change_event_occurred(
        subarray_node.subarray_node,
        "longRunningCommandResult",
        (pytest.command_result[1][0], Anything),
        lookahead=15,
    )
    exception_message = (
        "Exception occurred on the following devices: "
        "ska_mid/tm_leaf_node/sdp_subarray01: "
        "Timeout has occurred, command failed\n"
    )
    assert (
        exception_message
        in json.loads(assertion_data["attribute_value"][1])[1]
    )

    pytest.sdp_sim.SetDefective(RESET_DEFECT)
