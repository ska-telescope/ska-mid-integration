import pytest
from pytest_bdd import parsers, scenario, when

from tests.conftest import LOGGER
from tests.resources.test_support.common_utils.telescope_controls import (
    BaseTelescopeControl,
)

telescope_control = BaseTelescopeControl()


@pytest.mark.SKA_mid33
@scenario(
    "../features/tmc_dish/xtp-64935.feature",
    "TMC validates reconfigure functionality with real dish",
)
def test_multiple_configure_functionality():
    """
    Test TMC allows multiple configuration

    """


@when(parsers.parse("the command configure is issued with {input_json1}"))
def send_configure(json_factory, input_json1, subarray_node):
    configure_json1 = json_factory(input_json1)
    LOGGER.info("Invoking Configure command with input_json1")
    _, pytest.unique_id = subarray_node.execute_transition(
        "Configure", configure_json1
    )
    LOGGER.info("Configure1 is invoked successfully")


# @then("the subarray transitions to obsState READY")
# def check_for_ready(subarray_node, event_recorder):
#     # Verify ObsState is READY
#     LOGGER.info("Verifying obsState READY after Configure1")
#     wait_for_device_status_ready(subarray_node.subarray_node)
#     assert event_recorder.has_change_event_occurred(
#         subarray_node.subarray_node, "obsState", ObsState.READY, lookahead=20
#     )


@when(
    parsers.parse(
        "the next successive configure command is issued with {input_json2}"
    )
)
def send_next_configure(
    json_factory, input_json2, subarray_node, event_recorder
):
    configure_json1 = json_factory(input_json2)
    LOGGER.info("Invoking Configure command with input_json1")
    _, pytest.unique_id = subarray_node.execute_transition(
        "Configure", configure_json1
    )
    LOGGER.info("Configure1 is invoked successfully")


# @then("the subarray reconfigures changing its obsState to READY")
# def check_for_reconfigure_ready(subarray_node, event_recorder):
#
#     LOGGER.info("Verifying obsState READY after Configure2")
#
#     wait_for_device_status_ready(subarray_node.subarray_node)
#     assert event_recorder.has_change_event_occurred(
#         subarray_node.subarray_node, "obsState", ObsState.READY, lookahead=20
#     )
