"""Test module to verify timeout error propogation from Dish"""
import json

import pytest
from pytest_bdd import scenario, then, when
from ska_tango_testing.mock.placeholders import Anything

from tests.resources.test_harness.constant import (
    ERROR_PROPAGATION_DEFECT,
    RESET_DEFECT,
    tmc_dish_leaf_node1,
)
from tests.resources.test_harness.event_recorder import EventRecorder
from tests.resources.test_harness.helpers import prepare_json_args_for_commands
from tests.resources.test_harness.simulator_factory import SimulatorFactory
from tests.resources.test_harness.subarray_node import SubarrayNodeWrapper
from tests.resources.test_harness.utils.common_utils import JsonFactory
from tests.resources.test_harness.utils.enums import SimulatorDeviceType


@pytest.mark.SKA_mid
@scenario(
    "../features/test_harness/xtp_49324_dish_" + "error_propogation.feature",
    "Verify error propogation with defective dish",
)
def test_dish_configure_error_propagation():
    """
    Test case to verify error propogation for
    defective dish
    """


# from conftest.py
# @given("the telescope is in ON state")


# from conftest.py
# @given("TMC subarray is in ObsState IDLE")


@when("Dish 1 is set defective")
def set_dish_defective(simulator_factory: SimulatorFactory):
    """A method to set defect on simulated Dish 1

    Args:
        simulator_factory: fixture for SimulatorFactory class,
        which provides simulated subarray and master devices
    """
    pytest.dish_sim_1 = simulator_factory.get_or_create_simulator_device(
        SimulatorDeviceType.DISH_DEVICE
    )
    # Set dish 1 defective
    pytest.dish_sim_1.SetDefective(json.dumps(ERROR_PROPAGATION_DEFECT))


@when("I issue the Configure command to the TMC subarray")
def invoke_configure(
    subarray_node: SubarrayNodeWrapper,
    command_input_factory: JsonFactory,
    event_recorder: EventRecorder,
) -> None:
    """
    Invokes Configure command on TMC SubarrayNode
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


@then("Exception is propagated to TMC subarray on longRunningCommandResult")
def check_timeout_error(
    subarray_node: SubarrayNodeWrapper, event_recorder: EventRecorder
):
    """A method to check SubarrayNode.longRunningCommandResult attribute
    change for exception

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
        + f"{tmc_dish_leaf_node1}:"
    )
    assert (
        exception_message
        in json.loads(assertion_data["attribute_value"][1])[1]
    )

    pytest.dish_sim_1.SetDefective(RESET_DEFECT)
