"""Test module to verify timeout error propogation from Csp Subarray"""
import json

import pytest
from pytest_bdd import scenario, then, when
from ska_tango_testing.mock.placeholders import Anything

from tests.resources.test_harness.central_node_mid import CentralNodeWrapperMid
from tests.resources.test_harness.constant import (
    OBS_STATE_CONFIGURING_STUCK_DEFECT,
    RESET_DEFECT,
)
from tests.resources.test_harness.event_recorder import EventRecorder
from tests.resources.test_harness.helpers import (
    prepare_json_args_for_centralnode_commands,
)
from tests.resources.test_harness.simulator_factory import SimulatorFactory
from tests.resources.test_harness.utils.common_utils import JsonFactory
from tests.resources.test_harness.utils.enums import SimulatorDeviceType
from tests.resources.test_support.constant import tmc_csp_master_leaf_node


@pytest.mark.batch1
@pytest.mark.SKA_mid
@scenario(
    "../features/test_harness/xtp_49365_"
    + "test_release_resources_error_propagation.feature",
    "Verify error propogation with defective CSP Subarray on ReleaseResources",
)
def test_csp_subarray_release_resources_error_propagation():
    """
    Test case to verify error propogation for
    defective Csp Subarray when ReleaseResources command invoked.
    """


@when("CSP subarray is set defective")
def set_csp_subarray_defective(simulator_factory: SimulatorFactory):
    """A method to set defect on simulated
    CSP Subarray

    Args:
        simulator_factory: fixture for SimulatorFactory class,
        which provides simulated subarray and master devices
    """
    pytest.csp_sim = simulator_factory.get_or_create_simulator_device(
        SimulatorDeviceType.MID_CSP_DEVICE
    )
    # Set csp defective
    pytest.csp_sim.SetDefective(json.dumps(OBS_STATE_CONFIGURING_STUCK_DEFECT))


@when("I issue the ReleaseResources command to the TMC")
def invoke_release_resources(
    central_node_mid: CentralNodeWrapperMid,
    command_input_factory: JsonFactory,
    event_recorder: EventRecorder,
) -> None:
    """
    Invokes ReleaseResources command on TMC.
    """
    event_recorder.subscribe_event(
        central_node_mid.central_node, "longRunningCommandResult"
    )
    release_input_json = prepare_json_args_for_centralnode_commands(
        "release_resources_mid", command_input_factory
    )
    pytest.command_result = central_node_mid.perform_action(
        "ReleaseResources", release_input_json
    )


@then("Exception is propagated to TMC on longRunningCommandResult")
def check_timeout_error(
    central_node_mid: CentralNodeWrapperMid, event_recorder: EventRecorder
):
    """A method to check SubarrayNode.longRunningCommandResult attribute
    change for exception

    Args:
        subarray_node : A fixture for SubarrayNode tango device class
        event_recorder: A fixture for EventRecorder class
    """
    assertion_data = event_recorder.has_change_event_occurred(
        central_node_mid.central_node,
        "longRunningCommandResult",
        (pytest.command_result[1][0], Anything),
        lookahead=15,
    )
    exception_message = (
        "Exception occurred on the following devices: "
        f"{tmc_csp_master_leaf_node}: "
    )
    assert (
        exception_message
        in json.loads(assertion_data["attribute_value"][1])[1]
    )

    pytest.csp_sim.SetDefective(RESET_DEFECT)
